import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";

import { apiGet, apiPost, getAuthToken, setAuthToken } from "../api";

type User = {
  id: string;
  email: string;
};

type Debt = {
  id: string;
  title: string;
  description?: string | null;
  status: string;
  created_by: string;
  created_at?: string | null;
  updated_at?: string | null;
};

type DebtListResponse = {
  items: Debt[];
};

export default function Dashboard() {
  const history = useHistory();
  const [user, setUser] = useState<User | null>(null);
  const [debts, setDebts] = useState<Debt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  const token = getAuthToken();

  useEffect(() => {
    if (!token) {
      history.push("/login");
      return;
    }

    const load = async () => {
      setLoading(true);
      setError(null);

      const meResult = await apiGet<User>("/auth/me", token);
      if (!meResult.ok) {
        setAuthToken(null);
        history.push("/login");
        return;
      }

      setUser(meResult.data);

      const debtResult = await apiGet<DebtListResponse>(
        `/debts?created_by=${meResult.data.id}`,
        token
      );
      if (!debtResult.ok) {
        setError(debtResult.error);
        setDebts([]);
      } else {
        setDebts(debtResult.data.items || []);
      }

      setLoading(false);
    };

    load();
  }, [history, token]);

  const onCreateDebt = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!token) {
      history.push("/login");
      return;
    }

    setCreating(true);
    setError(null);

    const result = await apiPost<Debt>(
      "/debts",
      {
        title,
        description,
      },
      token
    );

    if (!result.ok) {
      setError(result.error);
      setCreating(false);
      return;
    }

    setDebts((prev) => [result.data, ...prev]);
    setTitle("");
    setDescription("");
    setCreating(false);
  };

  const onLogout = () => {
    setAuthToken(null);
    history.push("/login");
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Signed in as: {user?.email}</p>
      <button onClick={onLogout}>Logout</button>

      <h2>Create debt</h2>
      <form onSubmit={onCreateDebt}>
        <div>
          <label htmlFor="title">Title</label>
          <input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="description">Description</label>
          <input
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit" disabled={creating}>
          {creating ? "Creating..." : "Create"}
        </button>
      </form>

      {error && <p>Error: {error}</p>}

      <h2>Your debts</h2>
      {debts.length === 0 ? (
        <p>No debts yet.</p>
      ) : (
        <ul>
          {debts.map((debt) => (
            <li key={debt.id}>
              <strong>{debt.title}</strong> ({debt.status})
              {debt.description ? ` - ${debt.description}` : ""}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
