
# TalentScout AI - Intelligent Hiring Assistant

This project is a smart, conversational hiring assistant designed to make the first step of the recruitment process feel a little more human.

The main goal was to build an AI that can handle initial candidate screenings smoothly. It chats with candidates to gather essential information and then, based on their unique tech skills, asks relevant technical questions. It's built in such a way that it makes the whole process feel more like a real conversation and less like filling out a form.


## Installation Instructions

Getting the assistant up and running on your local machine is pretty straightforward. Just follow these steps.

#### Prerequisites

* Python 3.8 or higher
* An OpenAI API key

#### Step 1: Clone the Repository

First, grab the code from the repository and navigate into the folder.

#### Step 2: Set Up a Virtual Environment

Create a virtual environment.

  * On Windows:

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

  * On Mac/Linux:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

#### Step 3: Installation

Install all the necessary libraries.

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Your API Key

In the file named `.env` in the main project directory is where you'll securely store your OpenAI API key.

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

**Important:** Make sure you replace the placeholder with your real key

#### Step 5: Run the App

You're all set. To launch the application, navigate into the `src` folder and run the Streamlit command.

```bash
cd src
streamlit run app.py
```

Your browser should open a new tab with the TalentScout AI ready to chat.

##  Usage Guide

Interacting with the chatbot is designed to be as simple as having a conversation.

1.  **Start the Chat:** When you launch the app, the AI assistant will greet you and explain the process.
2.  **Provide Your Info:** The bot will ask for your information one piece at a time, starting with your name, then email, phone number, and so on.
3.  **Share Your Skills:** When asked for your tech stack, list out the programming languages, frameworks, and tools you're comfortable with.
4.  **Answer Technical Questions:** Based on your tech stack, the bot will generate a few technical questions for you to answer.
5.  **Wrap Up:** Once you're done, the bot will give you a summary and explain the next steps. You can end the conversation at any time by typing "bye" or "exit".


##  Technical Details

Here's the technical decisions that power the assistant.

  * **Model:**

      * The application currently uses `gpt-3.5-turbo` by default, which offers a great balance of speed, intelligence, and cost-effectiveness.

  * **Architecture - Multi-Agent System:**
    I've built a system of specialized agents that work together. This makes the code cleaner and the chatbot smarter.

      * **`HiringAssistant`:** This is the main class that manages the conversation flow and directs tasks to the right agent.
      * **`ConversationAgent`:** This agent's job is to generate the acknowledgements after you provide a piece of information, making the chat feel less robotic.
      * **`ValidationAgent`:** A crucial agent that checks your input. It ensures that an email looks like an email and a phone number contains digits, providing helpful feedback if something is wrong.
      * **`QuestionGenerationAgent`:**  It uses a **Retrieval-Augmented Generation (RAG)** approach to create technical questions. It first tries to retrieve high-quality, pre-written questions from its internal knowledge base for common technologies. If your tech stack is more niche, it then augments this by generating custom questions using the LLM.

-----

## Prompt Design

  * **The System Prompt :** The `SYSTEM_PROMPT` acts as the AI's core set of rules and its personality. It instructs the bot to be professional, friendly, encouraging, and, most importantly, what topics to avoid (like personal opinions).

  * **RAG for Question Generation:** The `QuestionGenerationAgent` uses a RAG approach. It has a built-in knowledge base of great questions for popular technologies like Python, React, and AWS. This ensures question quality and speed. For less common technologies, it uses the `QUESTION_GENERATION_PROMPT` to ask the LLM to create new, relevant questions on the fly.

  * **Clear Validation Prompts:** When the `ValidationAgent` catches an error, it doesn't just say "Invalid." It uses a set of `VALIDATION_PROMPTS` to give you a clear example of the correct format, like `(e.g., john.doe@example.com)`. This makes the user experience much smoother.



##  Challenges & Solutions

Few challenges faced were:

  * Making the chatbot feel less like a rigid script.

      * **Solution:** I introduced the `ConversationAgent`. Its only job is to provide short, warm acknowledgements ("Thanks for sharing that\!") between the main questions. This simple addition breaks up the monotony and makes the flow feel much more natural.

  * Generating high-quality technical questions for any possible tech stack.

      * **Solution:** It creates a knowledge base of curated questions for common technologies. It only needs to use the more resource-intensive LLM for unique or uncommon tech stacks, giving the best of both worlds.

  * Preventing the user from getting stuck if they provide invalid input.

      * **Solution:** The `ValidationAgent` was designed to be helpful but not a blocker. After two failed validation attempts for a piece of information, the system is designed to accept the input as-is and move on to the next question. This prevents user frustration and keeps the conversation moving.

<!-- end list -->

```

```
