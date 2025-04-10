# Pick n Pay Lesotho: Distributed Online Shopping Database Application

Project Overview
This project is aimed at developing a distributed database application for Pick n Pay Lesotho. The application will manage products, customers, orders, payments, and other critical functions of an online shopping system. The solution will utilize a heterogeneous database system to meet the requirement for distributed databases, incorporating both PostgreSQL and MongoDB.

Objectives:
Design and implement a distributed database to manage products, customers, orders, and payments.

Develop a secure and user-friendly web application for customers to browse products, add to the shopping cart, and complete orders.

Ensure the application is scalable, with features like order tracking, sales reporting, and payment integration.

Provide an admin interface to manage products, view sales insights, and control customer data.

Integrate secure payment gateways and ensure safe transaction processing.

Key Features
Product Management: View and manage product listings, including stock levels and categories.

Shopping Cart: Add products to the cart, modify quantities, and proceed to checkout.

Order Processing: Track orders and update stock levels in real-time.

User Accounts: Secure registration, login, and role-based access (admin, customer).

Sales Reporting: Generate detailed sales reports by product, category, and time period.

Payment Integration: Simulated secure payment gateway for transactions (e.g., PayPal, Stripe).

Multi-Database Architecture: Uses PostgreSQL for structured data and MongoDB for flexible data management.

Technology Stack
Backend:
Django (Python framework): For the web application, using Django’s ORM for PostgreSQL and integrating MongoDB using djongo or mongoengine.

PostgreSQL: For managing relational data, including product listings, customer data, and orders.

MongoDB: For managing unstructured data, such as customer reviews, logs, and product activities.

Django REST Framework: For creating APIs (if needed for a future mobile app or additional integrations).

Frontend:
Bootstrap: For designing a responsive and user-friendly UI.

HTML/CSS/JavaScript: For custom front-end needs and interactive elements.

Security:
Django Authentication: For secure login and user management.

JWT: For handling user sessions and role-based access.

Payment Gateways: Integration with Stripe or PayPal (for simulation).

Deployment:
Heroku / Render: For cloud-based deployment.

Docker (optional): For containerizing the application, ensuring a consistent development and production environment.

Database Design
The database schema is designed to manage the following entities:

Products: Stores product details such as name, description, price, stock levels, and category.

Customers: Contains customer information, including name, email, shipping, and billing addresses.

Orders: Tracks customer orders, including order total, date, and status.

Order Items: Records individual items within an order, with their respective quantity and unit price.

Shopping Cart: Allows customers to add products to their cart before proceeding to checkout.

Payment Transactions: Stores information about payment statuses and transaction details.

The PostgreSQL database will manage relational data, and MongoDB will store semi-structured data like product reviews and activity logs.

Setup Instructions
Prerequisites:
Python 3.8+

PostgreSQL and MongoDB installed locally or use cloud instances (e.g., Heroku for PostgreSQL, MongoDB Atlas for MongoDB).

Node.js and npm (for frontend dependencies, if applicable).
