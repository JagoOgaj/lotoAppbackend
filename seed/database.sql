-- Table pour stocker les rôles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,                                      -- Identifiant unique du rôle
    role_name VARCHAR UNIQUE NOT NULL                           -- Nom du rôle (par exemple, 'user', 'admin')
);

-- Table pour stocker les utilisateurs
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                                      -- Identifiant unique de l'utilisateur
    first_name VARCHAR NOT NULL,                                -- Prénom de l'utilisateur
    last_name VARCHAR NOT NULL,                                 -- Nom de famille de l'utilisateur
    email VARCHAR UNIQUE NOT NULL,                              -- Adresse e-mail de l'utilisateur
    password_hash VARCHAR NOT NULL,                             -- Mot de passe haché                                            
    role_id INT REFERENCES roles(id) ON DELETE SET NULL,        -- Référence au rôle de l'utilisateur
    created_at TIMESTAMP,                                       -- Date de création du compte
    updated_at TIMESTAMP                                        -- Date de mise à jour
);

-- Table pour stocker les tirages de loterie
CREATE TABLE lotteries (
    id SERIAL PRIMARY KEY,                                      -- Identifiant unique du tirage
    name VARCHAR NOT NULL,                                      -- Nom du tirage
    start_date TIMESTAMP NOT NULL,                              -- Date et heure de début du tirage
    end_date TIMESTAMP NOT NULL,                                -- Date et heure de fin du tirage
    status VARCHAR NOT NULL,                                    -- Statut du tirage (upcoming, finished)
    max_participants INT NOT NULL,                              -- Nombre maximum de participants
    created_at TIMESTAMP,                                       -- Date de création du tirage
    updated_at TIMESTAMP                                        -- Date de mise à jour
);

-- Table pour stocker les participations aux tirages
CREATE TABLE entries (
    id SERIAL PRIMARY KEY,                                      -- Identifiant unique de la participation
    user_id INT REFERENCES users(id) ON DELETE CASCADE,         -- Référence à l'utilisateur
    lottery_id INT REFERENCES lotteries(id) ON DELETE CASCADE,  -- Référence au tirage
    numbers VARCHAR NOT NULL                                    -- Numero classique
    lucky_number VARCHAR                                        -- Numero chance
    UNIQUE (user_id, lottery_id)                                -- Un utilisateur ne peut participer qu'une seule fois à un tirage
);

-- Table pour stocker les résultats des tirages
CREATE TABLE lottery_results (
    id SERIAL PRIMARY KEY,                                      -- Identifiant unique du résultat
    lottery_id INT REFERENCES lotteries(id) ON DELETE CASCADE,  -- Référence au tirage
    winning_numbers VARCHAR NOT NULL,                           -- Numéros gagnants
    
);