-- Upewnij się, że rozszerzenie pgcrypto jest aktywne
create extension if not exists "pgcrypto";

create table users (
    id uuid primary key default gen_random_uuid(),
    email varchar(255) unique not null,
    password_hash varchar(255) not null,
    created_at timestamp default now()
);

create table debts (
    id uuid primary key default gen_random_uuid(),
    title varchar(255) not null,
    description text,
    created_by uuid references users(id),
    created_at timestamp default now()
);

create table debt_participants (
    id uuid primary key default gen_random_uuid(),
    debt_id uuid references debts(id) on delete cascade,
    from_user_id uuid references users(id),
    to_user_id uuid references users(id),
    amount numeric(12,2) not null,
    description text,
    created_at timestamp default now()
);

create table payments (
    id uuid primary key default gen_random_uuid(),
    debt_participant_id uuid references debt_participants(id) on delete cascade,
    paid_by uuid references users(id),
    amount numeric(12,2) not null,
    paid_at timestamp default now(),
    note text
);
