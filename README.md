# AI-Powered Chatbot for Supplier and Product Information

## Overview  
This project is an AI-powered chatbot that allows users to query a supplier and product database using natural language.  
It retrieves relevant product and supplier details from a MySQL database and summarizes them using **Gemma-2-9b-it** via the **Groq API**.  
The chatbot is built using **LangGraph** for agent workflows and **FastAPI** for backend communication.  

![chatbot-screen](https://github.com/darknight2163/DBChatbot/blob/main/resource/screen.gif)

## Features  
✅ **Natural Language Querying** – Users can ask about products, suppliers, and categories.  
✅ **LLM-Powered Summarization** – Responses are enhanced using **Gemma-2-9b-it**.  
✅ **Real-Time Conversations** – The chatbot maintains a session-based conversation history.  
✅ **Responsive UI** – Built with **React, Vite, and Tailwind CSS** for a smooth experience.  
✅ **Efficient Database Queries** – Uses **MySQL** for structured storage of products and suppliers.  

## Tech Stack  
🔹 **Backend**: Python, FastAPI, LangGraph, Groq API (Gemma-2-9b-it), MySQL  
🔹 **Frontend**: React, Vite, Tailwind CSS, Axios  
🔹 **Database**: MySQL  

These are the tables(products, suppliers) of the database(`ProductSuppliers.db`) respectively:
, while 
| ID  | Name           | Brand | Price   | Category          | Description                        | Supplier ID |
|----|--------------|------|--------|----------------|--------------------------------|-------------|
| 1  | Smartphone    | X    | 699.99  | Electronics      | Latest model with AI camera    | 1           |
| 2  | Refrigerator  | Y    | 1199.99 | Home Appliances  | Energy-efficient cooling       | 1           |
| 3  | Sofa Set      | Z    | 499.99  | Furniture        | Comfortable 3-seater           | 2           |
| 4  | Dining Table  | Z    | 899.99  | Furniture        | Solid wood with six chairs     | 2           |
| 5  | Organic Juice | W    | 5.99    | Groceries        | Freshly squeezed organic juice | 3           |

- The "**products**" table stores details about products, including **brand, price, category, and descriptions**.

| ID  | Name | Contact Info         | Product Categories               |
|----|------|----------------------|----------------------------------|
| 1  | A    | contactA@example.com | Electronics, Home Appliances    |
| 2  | B    | contactB@example.com | Furniture, Decor                |
| 3  | C    | contactC@example.com | Groceries, Beverages            |

- The "**suppliers**" table holds supplier information such as **contact details and product categories they provide**.
---

## Setup & Installation  
(You only need to setup frontend and backend for testing purpose, rest are managed...).
### 1️⃣ Backend Setup  
#### **Prerequisites**  
- Python 3.9+  
- MySQL installed & running  

#### **Steps to Run**  
##### Clone the repository
```
git clone https://github.com/your-username/chatbot-assessment.git
```
```
cd chatbot-assessment/backend
```

##### Create a virtual environment
```
python -m venv venv
```
```
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

##### Install dependencies
```
pip install -r requirements.txt
```

##### Run the backend
```
python api.py
```

### 3️⃣ Frontend Setup
#### **Prerequisites**  
- node.js 18+ [install from here](https://nodejs.org/en/download)
- vite
  
#### **Steps to Run**  
```
cd ../frontend
```

##### Install dependencies
```
npm install
```

##### Start the frontend
```
npm run dev
```
The app will be available at `http://localhost:5173/` (backend will be running at `http://localhost:8000/`).

## Usage
Try these sample queries:

❓```Show me all the products.```

❓```name all products under brand X```

❓```Which suppliers provide furniture?```

❓```Give me details of product 2, 3 and 4.```

❓```Calculate the average price of all the available products.```

❓```which supplier should I contact for electronics? Also give me details for contacting them```

❓```which supplier is selling the most number of products? Also give me the names of all that products.```

❓```Which is the least priced product?```



  
