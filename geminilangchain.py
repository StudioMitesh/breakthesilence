from dotenv import load_dotenv
import os
from gtts import gTTS
import whisper
import warnings
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain.vectorstores import FAISS


designation = []

#Instantiate Context and Vector Store
TEXT_FILE_PATH = "JohnProfile.txt"
with open(TEXT_FILE_PATH, "r", encoding="utf-8") as file:
    text = file.read()

# Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,  # Adjust based on your needs
    chunk_overlap=50,  # Overlap between chunks
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_text(text)

#Embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store = FAISS.from_texts(chunks, embedding_model)

# Initialize the retriever
retriever = vector_store.as_retriever()

# Optionally, configure the retriever
retriever.search_kwargs.update({
    "k": 2,  # Number of relevant chunks to retrieve
})


#instantiate model
load_dotenv()
llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv('API_KEY'))

#Output Parser
output_parser = StrOutputParser()

#Define prompt
gen_prompt = ChatPromptTemplate.from_messages([
    ("system", 'You are an AI assistant designed to help non-verbal individuals communicate. All responses should be said as if you are the user. '
        'Do not make up additional details. Do not request more context, but feel free to elaborate slightly without making up information.'
        'Please include proper language pleasentries in your output. You will receive input representing a category and subcategory.'
        'Your task is to interpret these and generate natural, context-appropriate responses that the user might want to communicate.'
        'Be concise, clear, and empathetic in your responses. Always prioritize the user intent and generate responses that sound natural when spoken aloud.'
        'Do not place quotes at the beginning or end of your response. Try and elaborate slightly and use filler words on your output to make the text more humanistic.'
        'Use these retrieved documents as context whenever necessary: {retrieved_documents}'),
    MessagesPlaceholder(variable_name="messages"),
    ("human","user_input"),
])


#memory instantiation
workflow = StateGraph(state_schema=MessagesState)

#Define Chain
chain = gen_prompt | llm_model | output_parser

#Calling model chain
def call_llm(state: MessagesState):
    human_messages = [msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)]
    user_input = human_messages[-1] if human_messages else ""

    # Retrieve relevant documents based on the user input
    retrieved_docs = retriever.get_relevant_documents(user_input)
    
    # Concatenate the content of retrieved documents
    retrieved_content = "\n\n".join([doc.page_content for doc in retrieved_docs])
    print(retrieved_content)

    response = chain.invoke({"messages": state["messages"], "user_input": user_input, "retrieved_documents": retrieved_content})

    ai_message = AIMessage(content=response)
    new_messages = state["messages"] + [ai_message]
    return {"messages": new_messages}

# node and Edge
workflow.add_node("llm_model", call_llm)
workflow.add_edge(START, "llm_model")

#in-memory checkpointer
memory = MemorySaver()
flow = workflow.compile(checkpointer=memory)

#Speech to Text
audio_model = whisper.load_model("base")
question = "What is the meaning of life?"
def speech_to_text(audio_file):
    global question
    audio_result = audio_model.transcribe(audio_file)
    print(audio_result)
    question = audio_result['text']


#send message to app
def send_message(flow, user_content, thread_id="1"):
    # Create the HumanMessage
    human_message = HumanMessage(content=user_content)
    
    # Invoke the app
    out = flow.invoke(
        {"messages": [human_message]},
        config={"configurable": {"thread_id": thread_id}},
    )
    
    # Extract and return the AI's response
    if "messages" in out and len(out["messages"]) > 0:
        last_message = out["messages"][-1]
        if isinstance(last_message, AIMessage):
            return last_message.content
    return "No response received."

# Send initial message
#response = send_message(app, "I like eggs")
#print("AI Response:", response)

# Send follow-up message
#response = send_message(app, "What did I just say?", thread_id="1")
#print("AI Response:", response)

#question = "Do you like dogs"

def user_call(sequence) -> str:
    additional_prompt = ""
    if (sequence[0] == 1):
        category = "Wants/Needs"
        if (sequence[1] == 1):
            subcategory = "Food"
            additional_prompt = "List some of my favorite foods"
        elif (sequence[1] == 2):
            subcategory = "Drink"
            additional_prompt = "List some of my favorite drinks"
        elif (sequence[1] == 3):
            subcategory = "Activity"
            additional_prompt = "List some of my favorite activities"
        elif (sequence[1] == 4):
            subcategory = "Help/Assistance"
        elif (sequence[1] == 5):
            subcategory = "Reiterate previous statement with emphasis"
        return f"You are assisting someone who is nonverbal. Based on the category {category} and the subcategory {subcategory}, generate a natural sentence or phrase they might use to communicate this need. Keep the tone simple and polite and {additional_prompt} using the retrieved documents."
    if (sequence[0] == 2):
        category = "Medical Status"
        if (sequence[1] == 1):
            subcategory = "feeling better"
        elif (sequence[1] == 2):
            subcategory = "feeling worse"
        elif (sequence[1] == 3):
            subcategory = "Do not need a doctor"
        elif (sequence[1] == 4):
            subcategory = "Need a doctor"
            additional_prompt = "List my favorite doctor"
        elif (sequence[1] == 5):
            subcategory = "Reiterate previous statement with emphasis using the message history, this should not be a generic emphasis"
        return f"You are assisting someone who is nonverbal. Based on the category {category} and the subcategory {subcategory}, generate a natural sentence or phrase they might use to describe their current medical condition or request medical attention. Keep the tone simple and clear, and if it is non-empty answer the, additional prompt: {additional_prompt} using the retrieved documents. Feel free to elaborate slightly and use filler words to make the text more humanistic."
    if (sequence[0] == 3):
        category = "Affirming"
        if (sequence[1] == 1):
            task = f"Answer the {question} in an affirming way. Ask them their opinon"
        elif (sequence[1] == 2):
            task = f"Answer the {question} in an affirming way."
        elif (sequence[1] == 3):
            task = f"Agree strongly with {question}"
        elif (sequence[1] == 4):
            task = f"Agree but not with much confidence to the {question}"
        elif (sequence[1] == 5):
            task = "Reiterate previous statement with emphasis using the message history, this should not be a generic emphasis, and should not be just a restatement of the previous"
        return task
    if (sequence[0] == 4):
        category = "Negative"
        if (sequence[1] == 1):
            task = f"Answer the {question} in an disaffirming way. Ask them their opinon"
        elif (sequence[1] == 2):
            task = f"Answer the {question} in an disaffirming way."
        elif (sequence[1] == 3):
            task = f"Disagree strongly with {question}"
        elif (sequence[1] == 4):
            task = f"Disagree but not with much confidence to the {question}"
        elif (sequence[1] == 5):
            task = "Reiterate previous statement with emphasis using the message history, this should not be a generic emphasis, and should not be just a restatement of the previous"
        return task
    if (sequence[0] == 5):
        category = "Questions/Miscellaneous"
        if (sequence[1] == 1):
            subcategory = "The user does not understand, ask the other person to repeat?"
        elif (sequence[1] == 2):
            subcategory = "Ask for a few minutes to think"
        elif (sequence[1] == 3):
            subcategory = "Thank the other person"
        elif (sequence[1] == 4):
            subcategory = "Imply uncertainty, that the user is not sure"
        elif (sequence[1] == 5):
            subcategory = "End the conversation"
    return f"You are assisting someone who is nonverbal. Based on the category {category} and the subcategory {subcategory}, generate a natural sentence or phrase they might use in this situation. Keep the tone polite and clear."

'''
prompt = user_call([1,2])
response1 = send_message(app, prompt)
print("AI Response:", response1)

prompt = user_call([1,5])
response2 = send_message(app, prompt)
print("AI Response:", response2)

prompt = user_call([1,7])
response3 = send_message(app, prompt)
print("AI Response:", response3)
def text_to_speech(text, lang='ko'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("response.mp3")
    os.system("afplay response.mp3")

text_to_speech(response1)
time.sleep(1)
text_to_speech(response2)
time.sleep(1)
text_to_speech(response3)

'''
'''prompt = user_call([1,2])
response = send_message(app, prompt)
print("AI Response:", response)
'''
def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("response.mp3")
    os.system("afplay response.mp3")

#text_to_speech(response)





'''for text in chain.stream(
    {
        "history": [
            HumanMessage(
                content="Translate from English to French: I love programming."
            ),
            AIMessage(content="J'adore la programmation."),
            HumanMessage(content="what language were you just speaking?"),
        ],
    }
):
    print(text, flush=True)'''