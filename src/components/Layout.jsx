import React from "react";
import { Link } from "react-router-dom";

const Layout = ({ children }) => (
  <div className="min-h-screen flex flex-col">
    <header className="bg-indigo-600 text-white p-4 flex justify-between items-center">
      <h1 className="text-xl font-bold">My App</h1>
      <nav>
        <Link className="mr-4 hover:underline" to="/">Home</Link>
        <Link className="mr-4 hover:underline" to="/dashboard">Dashboard</Link>
        <Link className="hover:underline" to="/profile">Profile</Link>
      </nav>
    </header>
    <main className="flex-1 p-4">{children}</main>
    <footer className="bg-gray-200 text-center p-2">
      © {new Date().getFullYear()} My App
    </footer>
  </div>
);

export default Layout;
