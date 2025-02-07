import { useRef } from "react";

const ChatForm = ({ chatHistory, setChatHistory, generateBotResponse }) => {
    const inputRef = useRef();

    const handleFormSubmit = (e) => {
        e.preventDefault();
        const userMessage = inputRef.current.value.trim();
        if (!userMessage) return;
        inputRef.current.value = "";

        // Update chat history with the user's message
        setChatHistory((history) => [...history, { role: "user", text: userMessage }]);
        
        // Delay 600 ms before "thinking..." and generate response
        setTimeout(() => {
            // Add a thinking ... placeholder for bot's response
            setChatHistory((history) => [...history, { role: "model", text: "Analyzing the database ..." }]);
            // Call the function to generate bot's response
            generateBotResponse([...chatHistory, { role: "user", text: userMessage }]);
        }, 600);
    };

    return (
        <form action="#" className="chat-form" onSubmit={handleFormSubmit}>
            <input ref={inputRef} type="text" placeholder="Ask something..." className="message-input" required />
            <button className="material-symbols-rounded">arrow_upward</button>
          </form>
    );
};

export default ChatForm;