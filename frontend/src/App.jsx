// Copyright (c) 2025 Shivam Kumar
// All rights reserved. Unauthorized copying, distribution, or modification is prohibited.

import { useEffect, useState, useRef } from "react";
import ChatbotIcon from "./components/ChatbotIcon";
import ChatForm from "./components/ChatForm";
import ChatMessage from "./components/ChatMessage";

const App = () => {
  const [chatHistory, setChatHistory] = useState([]);
  const [showChatbot, setshowChatbot] = useState(true);

  const chatBodyRef = useRef();


  const generateBotResponse = async (history) => {
    //Helper function to update chat history
    const updateHistory = (text) => {
      console.log("updating history with response: ", text);
      setChatHistory((prev) => [...prev.filter((msg) => msg.text !== "Analyzing the database ..."), {role: "model", text}]);
    }

    // Format chat history to map as per API request
    // history = history.map(({role, text}) => ({role, parts: [{text}]}));

    const requestBody = JSON.stringify({
      input_message: history[history.length - 1].text //Send only last user input
    })

    const requestOptions = {
      method: "POST",
      headers: {"Content-Type": "application/json" },
      body: requestBody,
    }

    try {
      // make the API call to get the bot's response
      // const response = await fetch(import.meta.env.VITE_API_URL, requestOptions);
      const response = await fetch("http://localhost:8000/chat_query", requestOptions);
      const data = await response.json();
      if(!response.ok) throw new Error(data.error.message || "Something went wrong");

      // const apiResponseText = data.candidates[0].contents.parts[0].text.replace(/\*\*(.*?)\*\*/g, "$1").
      const apiResponseText = data.relevant_answer.trim();
      updateHistory(apiResponseText);
    }
    catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    //Auto scrolling when chat updates
    chatBodyRef.current.scrollTo({ top: chatBodyRef.current.scrollHeight, behavior: "smooth" });
  }, [chatHistory]);

  return (
    <div className={`container ${showChatbot ? "show-chatbot" : ""}`}>
      <button onClick={() => setshowChatbot(prev => !prev)} 
      id="chatbot-toggler">
        <span className="material-symbols-rounded">mode_comment</span>
        <span className="material-symbols-rounded">close</span>
      </button>

      <div className="chatbot-popup">
        {/* Chatbot header */}
        <div className="chat-header">
          <div className="header-info">
            <ChatbotIcon />
            <h2 className="logo-text">Database Chat</h2>
          </div>
          <button onClick={() => setshowChatbot(prev => !prev)}
          className="material-symbols-rounded">keyboard_arrow_down</button>
        </div>

        {/* Chatbot Body */ }
        <div ref={chatBodyRef} className="chat-body">
          <div className="message bot-message">
          <ChatbotIcon />
          <p className="message-text">
            Hey there! <br />How can I help you today?
            </p>
          </div>

          { /* Render the chat history dynamically */}
          {chatHistory.map((chat, index) =>(
            <ChatMessage key={index} chat={chat} />
          ))}
          </div>
        
        {/* Chatbot Footer */}
        <div className="chat-footer">
          <ChatForm chatHistory={chatHistory} setChatHistory={setChatHistory} generateBotResponse={generateBotResponse} />
        </div>
      </div>    
    </div>
  );
};

export default App;
