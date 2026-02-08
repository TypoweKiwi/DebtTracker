-- Upewnij się, że rozszerzenie pgcrypto jest aktywne
create extension if not exists "pgcrypto";

-- USERS TABLE
create table users (
    id uuid primary key default gen_random_uuid(),
    email varchar(255) unique not null,
    password_hash varchar(255) not null,
    created_at timestamp default now(),
    updated_at timestamp default now()
);

-- INDEX na email (dla szybkiego logowania)
create index idx_users_email on users(email);

-- DEBTS TABLE (główne długi)
create table debts (
    id uuid primary key default gen_random_uuid(),
    title varchar(255) not null,
    description text,
    created_by uuid not null references users(id) on delete cascade,
    status varchar(50) default 'open' check(status in ('open', 'settled', 'cancelled')),
    created_at timestamp default now(),
    updated_at timestamp default now()
);

-- INDEX na created_by (dla szybkiego query)
create index idx_debts_created_by on debts(created_by);
create index idx_debts_status on debts(status);

-- DEBT_PARTICIPANTS TABLE (kto komu jest winien)
create table debt_participants (
    id uuid primary key default gen_random_uuid(),
    debt_id uuid not null references debts(id) on delete cascade,
    from_user_id uuid not null references users(id) on delete cascade,
    to_user_id uuid not null references users(id) on delete cascade,
    amount numeric(12,2) not null check(amount > 0),
    description text,
    status varchar(50) default 'open' check(status in ('open', 'settled')),
    created_at timestamp default now(),
    updated_at timestamp default now()
);

-- INDEX na relacjach
create index idx_debt_participants_debt_id on debt_participants(debt_id);
create index idx_debt_participants_from_user on debt_participants(from_user_id);
create index idx_debt_participants_to_user on debt_participants(to_user_id);
create index idx_debt_participants_status on debt_participants(status);

-- PAYMENTS TABLE (historia wpłat)
create table payments (
    id uuid primary key default gen_random_uuid(),
    debt_participant_id uuid not null references debt_participants(id) on delete cascade,
    paid_by uuid not null references users(id) on delete cascade,
    amount numeric(12,2) not null check(amount > 0),
    paid_at timestamp default now(),
    note text,
    created_at timestamp default now()
);

-- INDEX na queries
create index idx_payments_debt_participant_id on payments(debt_participant_id);
create index idx_payments_paid_by on payments(paid_by);
create index idx_payments_paid_at on payments(paid_at);
