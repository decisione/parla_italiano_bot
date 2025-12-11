-- Create exercise_prompts table for varied exercise prompts
CREATE TABLE IF NOT EXISTS exercise_prompts (
    id SERIAL PRIMARY KEY,
    prompt TEXT NOT NULL
);

-- Insert initial exercise prompts in Italian (short versions)
INSERT INTO exercise_prompts (prompt) VALUES
    ('Prossimo:'),
    ('Nuovo:'),
    ('Prova questo:'),
    ('Vai:'),
    ('Avanti:'),
    ('Ora tocca a te:'),
    ('Un altro:'),
    ('Fai questo:'),
    ('Prosegui:'),
    ('Continua:'),
    ('Ecco:'),
    ('Pronti?'),
    ('Inizia:'),
    ('Prova:'),
    ('Sì, vai:');