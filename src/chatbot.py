"""
Core chatbot logic with Agent System and RAG capabilities.
Uses structured agent workflow instead of simple LLM calls.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from prompts.system_prompts import (
    SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT,
    FAREWELL_PROMPT,
    VALIDATION_PROMPTS
)

# Load environment variables
load_dotenv()


class ConversationAgent:
    """Agent responsible for managing conversation flow"""
    
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model
        self.name = "Conversation Manager"
    
    def process(self, message: str, context: Dict) -> str:
        """Process user message with context awareness"""
        current_stage = context.get('current_stage', 'greeting')
        
        # Generate contextual response
        prompt = f"""You are a friendly hiring assistant. 
Current stage: {current_stage}
Candidate has provided: {message}

Acknowledge their response warmly and naturally. Keep it brief (1-2 sentences).
Do not ask the next question - just acknowledge."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except:
            return "Thank you for sharing that!"


class ValidationAgent:
    """Agent responsible for input validation"""
    
    def __init__(self):
        self.name = "Validation Agent"
    
    def validate(self, stage: str, value: str) -> Tuple[bool, Optional[str]]:
        """Validate input based on stage"""
        value = value.strip()
        
        if stage == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, value):
                return True, None
            return False, VALIDATION_PROMPTS['email']
        
        elif stage == 'phone':
            if any(char.isdigit() for char in value):
                return True, None
            return False, VALIDATION_PROMPTS['phone']
        
        elif stage == 'experience':
            if value.lower() in ['fresher', 'fresh graduate', '0'] or any(char.isdigit() for char in value):
                return True, None
            return False, VALIDATION_PROMPTS['experience']
        
        elif stage == 'name':
            if len(value) >= 2:
                return True, None
            return False, "Please provide your full name (at least 2 characters)."
        
        elif stage == 'techstack':
            if len(value) >= 3:
                return True, None
            return False, VALIDATION_PROMPTS['techstack']
        
        # Default: accept any non-empty input
        if len(value) > 0:
            return True, None
        return False, f"Please provide your {stage}."


class QuestionGenerationAgent:
    """Agent responsible for generating technical questions using RAG"""
    
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model
        self.name = "Question Generator"
        self.knowledge_base = self._load_question_knowledge()
    
    def _load_question_knowledge(self) -> Dict[str, List[str]]:
        """RAG knowledge base for question generation"""
        return {
            'python': [
                "Explain the difference between a list and a tuple in Python. When would you use each?",
                "How do you handle exceptions in Python? Provide an example of a try-except block.",
                "What are Python decorators and how have you used them?",
                "Explain list comprehensions and give an example of when you'd use them."
            ],
            'javascript': [
                "What's the difference between 'let', 'var', and 'const' in JavaScript?",
                "Explain closures in JavaScript with a practical example.",
                "What is the event loop and how does it work?",
                "How does 'this' keyword work in different contexts?"
            ],
            'js': [  # Alternative name for JavaScript
                "What are arrow functions and how do they differ from regular functions?",
                "Explain promises and async/await in JavaScript.",
                "What is event bubbling and capturing?",
                "How do you handle asynchronous operations in JavaScript?"
            ],
            'react': [
                "What are React hooks? Which ones have you used most frequently?",
                "Explain the virtual DOM and how React uses it for optimization.",
                "What's the difference between state and props?",
                "How do you handle side effects in React applications?"
            ],
            'django': [
                "Explain Django's MVT (Model-View-Template) architecture.",
                "How does Django's ORM work? What are its advantages?",
                "Describe Django's middleware and when you'd create custom middleware.",
                "How do you handle authentication and authorization in Django?"
            ],
            'flask': [
                "What's the difference between Django and Flask?",
                "Explain Flask's application context and request context.",
                "How do you structure a large Flask application?",
                "How do you handle database migrations in Flask?"
            ],
            'sql': [
                "What's the difference between INNER JOIN and LEFT JOIN?",
                "Explain database indexing and when you would use it.",
                "How do you optimize a slow database query?",
                "What are transactions and why are they important?"
            ],
            'mysql': [
                "Explain the difference between MyISAM and InnoDB storage engines.",
                "How do you optimize MySQL queries for better performance?",
                "What is query caching in MySQL?",
                "How do you handle database replication in MySQL?"
            ],
            'postgresql': [
                "What are the advantages of PostgreSQL over MySQL?",
                "Explain JSONB data type and when you'd use it.",
                "How does PostgreSQL handle concurrent transactions?",
                "What are PostgreSQL extensions and which ones have you used?"
            ],
            'mongodb': [
                "Explain the difference between SQL and NoSQL databases.",
                "How does indexing work in MongoDB?",
                "What are the advantages and disadvantages of MongoDB?",
                "How do you design schemas in MongoDB?"
            ],
            'node': [
                "Explain the event-driven architecture of Node.js.",
                "What is the difference between synchronous and asynchronous operations in Node?",
                "How do you handle errors in Node.js applications?",
                "Explain the concept of middleware in Express.js."
            ],
            'express': [
                "How does Express.js middleware work?",
                "Explain routing in Express.js.",
                "How do you handle errors in Express applications?",
                "What are the best practices for structuring an Express.js application?"
            ],
            'docker': [
                "What is Docker and why is it useful in development?",
                "Explain the difference between a Docker image and a container.",
                "How do you optimize Docker images for production?",
                "What is Docker Compose and when would you use it?"
            ],
            'kubernetes': [
                "What is Kubernetes and what problems does it solve?",
                "Explain pods, services, and deployments in Kubernetes.",
                "How does Kubernetes handle scaling?",
                "What is the difference between Kubernetes and Docker Swarm?"
            ],
            'aws': [
                "Explain the difference between EC2, ECS, and Lambda.",
                "What is S3 and what are its use cases?",
                "How do you ensure security in AWS environments?",
                "Describe a CI/CD pipeline using AWS services."
            ],
            'git': [
                "Explain the difference between merge and rebase in Git.",
                "How do you resolve merge conflicts?",
                "What is a pull request and what's your review process?",
                "Explain Git branching strategies you've used."
            ],
            'java': [
                "Explain the concept of inheritance and polymorphism in Java.",
                "What is the difference between abstract classes and interfaces?",
                "How does garbage collection work in Java?",
                "Explain the Java Collections Framework."
            ],
            'spring': [
                "What is dependency injection in Spring?",
                "Explain the difference between @Component, @Service, and @Repository.",
                "How does Spring Boot simplify Spring development?",
                "What is Spring MVC and how does it work?"
            ],
            'typescript': [
                "What are the advantages of TypeScript over JavaScript?",
                "Explain interfaces and types in TypeScript.",
                "How does TypeScript handle type inference?",
                "What are generics in TypeScript?"
            ],
            'angular': [
                "What's the difference between Angular and React?",
                "Explain components, services, and modules in Angular.",
                "How does dependency injection work in Angular?",
                "What are Angular directives?"
            ],
            'vue': [
                "What's the difference between Vue and React?",
                "Explain the Vue component lifecycle.",
                "How does Vue's reactivity system work?",
                "What is Vuex and when would you use it?"
            ],
            'redis': [
                "What is Redis and what are its common use cases?",
                "Explain Redis data structures.",
                "How do you use Redis for caching?",
                "What is Redis pub/sub?"
            ],
            'graphql': [
                "What's the difference between REST and GraphQL?",
                "Explain queries, mutations, and subscriptions in GraphQL.",
                "What are the advantages of GraphQL?",
                "How do you handle errors in GraphQL?"
            ],
            'api': [
                "What are RESTful API best practices?",
                "How do you version APIs?",
                "Explain different HTTP methods and when to use them.",
                "How do you handle authentication in APIs?"
            ],
            'rest': [
                "What are the principles of REST architecture?",
                "Explain HTTP status codes and when to use them.",
                "How do you design RESTful endpoints?",
                "What is HATEOAS in REST?"
            ],
            'testing': [
                "What's the difference between unit testing and integration testing?",
                "How do you write testable code?",
                "Explain test-driven development (TDD).",
                "What testing frameworks have you used?"
            ],
            'ci/cd': [
                "What is CI/CD and why is it important?",
                "Explain your experience with CI/CD pipelines.",
                "What tools have you used for continuous integration?",
                "How do you handle deployments in your workflow?"
            ]
        }

    
    def generate_questions(self, tech_stack: str, num_questions: int = 4) -> List[str]:
        """Generate questions using RAG approach - distributed across all technologies"""
        tech_lower = tech_stack.lower()
        questions = []
        
        # Find all matching technologies in the tech stack
        matched_techs = []
        for tech in self.knowledge_base.keys():
            if tech in tech_lower:
                matched_techs.append(tech)
        
        if matched_techs:
            # Distribute questions evenly across all matched technologies
            questions_per_tech = max(1, num_questions // len(matched_techs))
            
            # Get questions from each matched technology
            for tech in matched_techs:
                tech_questions = self.knowledge_base[tech]
                questions.extend(tech_questions[:questions_per_tech])
            
            # If we still need more questions, add extras from first tech
            if len(questions) < num_questions:
                remaining = num_questions - len(questions)
                for tech in matched_techs:
                    if len(questions) >= num_questions:
                        break
                    extra_questions = self.knowledge_base[tech][questions_per_tech:]
                    questions.extend(extra_questions[:remaining])
                    remaining = num_questions - len(questions)
        
        # If we have enough from knowledge base, return them
        if len(questions) >= num_questions:
            return questions[:num_questions]
        
        # Otherwise, generate additional questions using LLM (RAG generation)
        remaining = num_questions - len(questions)
        if remaining > 0:
            generated = self._generate_custom_questions(tech_stack, remaining)
            questions.extend(generated)
        
        # If still not enough (rare case), add generic questions
        if len(questions) < num_questions:
            generic = [
                "Describe a challenging technical problem you've solved recently and your approach.",
                "How do you ensure code quality and maintainability in your projects?",
                "What's your process for learning new technologies or frameworks?",
                "How do you approach debugging complex issues in production environments?"
            ]
            questions.extend(generic[:num_questions - len(questions)])
        
        return questions[:num_questions]
    
    def _generate_custom_questions(self, tech_stack: str, num: int) -> List[str]:
        """Generate custom questions using LLM for uncommon tech stacks"""
        prompt = QUESTION_GENERATION_PROMPT.format(
            num_questions=num,
            tech_stack=tech_stack
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            questions = self._parse_questions(content)
            return questions
        except Exception as e:
            print(f"Error generating questions: {e}")
            return [
                "Describe a challenging technical problem you've solved recently.",
                "How do you approach debugging complex issues?",
                f"What best practices do you follow when working with {tech_stack}?"
            ]
    
    def _parse_questions(self, content: str) -> List[str]:
        """Parse questions from LLM response"""
        questions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+[\.\):]', line) or line.lower().startswith('question'):
                question = re.sub(r'^\d+[\.\):\s]+', '', line)
                question = re.sub(r'^Question\s+\d+[\:\s]+', '', question, flags=re.IGNORECASE)
                if question and len(question) > 15:
                    questions.append(question.strip())
        
        return questions


class HiringAssistant:
    """Main orchestrator using agent-based architecture"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the hiring assistant with agent system"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model
        
        # Initialize agents
        self.conversation_agent = ConversationAgent(self.client, self.model)
        self.validation_agent = ValidationAgent()
        self.question_agent = QuestionGenerationAgent(self.client, self.model)
        
        # State management
        self.conversation_history = []
        self.candidate_data = {}
        self.current_stage = 'greeting'
        
        # Stage configuration
        self.stages = [
            'greeting', 'name', 'email', 'phone',
            'experience', 'position', 'location',
            'techstack', 'questions', 'complete'
        ]
        
        self.stage_questions = {
            'name': "Great to meet you! What's your full name?",
            'email': "Thanks! What's your email address?",
            'phone': "And your phone number? (You can include country code)",
            'experience': "How many years of professional experience do you have? (If you're a fresher, just say 0 or 'fresher')",
            'position': "What position or role are you interested in?",
            'location': "Where are you currently located? (City, Country)",
            'techstack': """Now let's talk about your technical skills! 

What's your tech stack? Please list:
• Programming languages (e.g., Python, JavaScript, Java)
• Frameworks (e.g., React, Django, Spring)
• Databases (e.g., MySQL, MongoDB, PostgreSQL)
• Tools (e.g., Docker, Git, AWS)

You can list them separated by commas."""
        }
        
        # Track validation attempts
        self.validation_attempts = {}
    
    def start_conversation(self) -> str:
        """Start the conversation"""
        greeting = """Hello! 👋 I'm TalentScout's AI Hiring Assistant.

I'm here to help us get to know you better and understand your technical expertise. This initial screening will take about 10-15 minutes.

Here's what we'll cover:
• Your background and experience  
• Your technical skills  
• A few technical questions based on your expertise

Everything you share is confidential and used only for recruitment purposes.

Ready to begin? Please tell me your full name. 😊"""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })
        
        return greeting
    
    def process_message(self, user_message: str) -> str:
        """Process user message through agent system"""
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Route to appropriate handler
        if self.current_stage == 'greeting':
            response = self._handle_greeting(user_message)
        elif self.current_stage in ['name', 'email', 'phone', 'experience', 'position', 'location']:
            response = self._handle_info_collection(user_message)
        elif self.current_stage == 'techstack':
            response = self._handle_techstack(user_message)
        elif self.current_stage == 'questions':
            response = self._handle_technical_questions(user_message)
        elif self.current_stage == 'complete':
            response = self._handle_completion(user_message)
        else:
            response = "Let's continue with the interview."
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _handle_greeting(self, message: str) -> str:
        """Handle initial greeting - store as name directly"""
        # User's first message after greeting is their name
        self.candidate_data['name'] = message.strip()
        self.validation_attempts['name_attempts'] = 0
        self.current_stage = 'email'
        return self.stage_questions['email']
    
    def _handle_info_collection(self, message: str) -> str:
        """Handle information collection with validation"""
        stage = self.current_stage
        
        # Validate input using validation agent
        is_valid, error_message = self.validation_agent.validate(stage, message)
        
        if not is_valid:
            # Track attempts to prevent infinite loops
            attempt_key = f"{stage}_attempts"
            attempts = self.validation_attempts.get(attempt_key, 0)
            
            if attempts >= 2:
                # After 2 failed attempts, accept input and move on
                self.validation_attempts[attempt_key] = 0
                self.candidate_data[stage] = message.strip()
                return self._move_to_next_stage()
            
            # Increment attempts and return error
            self.validation_attempts[attempt_key] = attempts + 1
            return error_message
        
        # Valid input - reset attempts and store data
        self.validation_attempts[f"{stage}_attempts"] = 0
        self.candidate_data[stage] = message.strip()
        
        # Move to next stage
        return self._move_to_next_stage()
    
    def _move_to_next_stage(self) -> str:
        """Move to the next conversation stage"""
        current_index = self.stages.index(self.current_stage)
        next_stage = self.stages[current_index + 1]
        self.current_stage = next_stage
        
        if next_stage in self.stage_questions:
            return self.stage_questions[next_stage]
        
        return "Thank you!"
    
    def _handle_techstack(self, message: str) -> str:
        """Handle tech stack and generate questions"""
        # Validate tech stack
        is_valid, error_message = self.validation_agent.validate('techstack', message)
        
        if not is_valid:
            return error_message
        
        self.candidate_data['techstack'] = message.strip()
        
        # Generate questions using question agent (RAG)
        questions = self.question_agent.generate_questions(message, num_questions=4)
        self.candidate_data['questions'] = questions
        self.candidate_data['answers'] = []
        self.candidate_data['current_question'] = 0
        
        self.current_stage = 'questions'
        
        response = f"""Excellent! Based on your tech stack, I'd like to ask you some technical questions to better understand your expertise. ✨

We'll go through {len(questions)} questions. Take your time with each answer - there's no rush!

**Question 1:** {questions[0]}"""
        
        return response
    
    def _handle_technical_questions(self, message: str) -> str:
        """Handle technical Q&A"""
        # Store the answer
        self.candidate_data['answers'].append(message.strip())
        
        current_q = self.candidate_data['current_question']
        total_q = len(self.candidate_data['questions'])
        
        # Check if more questions remain
        if current_q < total_q - 1:
            self.candidate_data['current_question'] += 1
            next_q_num = current_q + 2
            next_question = self.candidate_data['questions'][current_q + 1]
            
            return f"""Great answer! Thank you for sharing that. 👍

**Question {next_q_num}:** {next_question}"""
        else:
            # All questions answered
            self.current_stage = 'complete'
            return self._generate_completion_message()
    
    def _generate_completion_message(self) -> str:
        """Generate completion message"""
        name = self.candidate_data.get('name', 'there')
        
        return f"""Thank you so much, {name}! 🎉

We've completed the initial screening. Here's what we covered:

✅ Personal Information
✅ Professional Experience: {self.candidate_data.get('experience', 'N/A')}
✅ Desired Position: {self.candidate_data.get('position', 'N/A')}
✅ Tech Stack: {self.candidate_data.get('techstack', 'N/A')}
✅ Technical Questions: {len(self.candidate_data.get('answers', []))} answered

**Next Steps:**
• Our recruitment team will review your profile and responses
• We'll carefully evaluate your technical answers
• You'll hear back from us within 3-5 business days

**Do you have any questions for us?**
If you have any questions about the role, company, or process, please feel free to ask! We'll get back to you via email within the next few days.

Otherwise, you can type 'bye' to end the conversation."""
    
    def _handle_completion(self, message: str) -> str:
        """Handle post-completion messages"""
        # Store their question/comment
        if 'final_questions' not in self.candidate_data:
            self.candidate_data['final_questions'] = []
        self.candidate_data['final_questions'].append(message.strip())
        
        return f"""Thank you for your question! I've recorded it for our team.

We'll review your question along with your application and get back to you via email within the next few days with a detailed response.

Is there anything else you'd like to know? Otherwise, feel free to type 'bye' to end the conversation. 

Have a great day! 👋"""
    
    def end_conversation(self) -> str:
        """Generate farewell message"""
        name = self.candidate_data.get('name', '')
        farewell = FAREWELL_PROMPT
        if name:
            farewell = farewell.replace("today", name)
        return farewell
    
    def get_conversation_summary(self) -> Dict:
        """Get conversation summary"""
        return {
            'candidate_data': self.candidate_data,
            'current_stage': self.current_stage,
            'total_messages': len(self.conversation_history),
            'questions_asked': len(self.candidate_data.get('questions', [])),
            'answers_provided': len(self.candidate_data.get('answers', []))
        }