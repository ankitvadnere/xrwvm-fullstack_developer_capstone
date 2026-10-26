import React, { useState } from "react";
import Header from "../Header/Header";
import "./Register.css";

const API_BASE = (process.env.REACT_APP_API_BASE || "/djangoapp").replace(/\/+$/, "");

export default function Register() {
  const [form, setForm] = useState({
    userName: "",
    firstName: "",
    lastName: "",
    email: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}/registration`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(form),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || data.message || "Registration failed. Check the server endpoint.");
      }
      setMessage(data.message || "Registration request completed.");
    } catch (error) {
      setMessage(error.message || "Unable to reach the registration service.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <Header />
      <main className="container py-5" style={{ maxWidth: 560 }}>
      <h1 className="mb-2">Create your account</h1>
      <p className="text-muted mb-4">Join Cars Dealership to share and read dealership reviews.</p>
      <form onSubmit={handleSubmit} className="card card-body shadow-sm">
        <label className="form-label" htmlFor="userName">Username</label>
        <input className="form-control mb-3" id="userName" name="userName" value={form.userName} onChange={handleChange} autoComplete="username" placeholder="Username" required />

        <label className="form-label" htmlFor="firstName">First Name</label>
        <input className="form-control mb-3" id="firstName" name="firstName" value={form.firstName} onChange={handleChange} autoComplete="given-name" placeholder="First Name" required />

        <label className="form-label" htmlFor="lastName">Last Name</label>
        <input className="form-control mb-3" id="lastName" name="lastName" value={form.lastName} onChange={handleChange} autoComplete="family-name" placeholder="Last Name" required />

        <label className="form-label" htmlFor="email">Email</label>
        <input className="form-control mb-3" id="email" name="email" type="email" value={form.email} onChange={handleChange} autoComplete="email" placeholder="email" required />

        <label className="form-label" htmlFor="password">Password</label>
        <input className="form-control mb-4" id="password" name="password" type="password" value={form.password} onChange={handleChange} autoComplete="new-password" minLength={8} placeholder="Password" required />

        <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Registering…" : "Register"}</button>
        {message && <p className="mt-3 mb-0" role="status">{message}</p>}
      </form>
      </main>
    </div>
  );
}
