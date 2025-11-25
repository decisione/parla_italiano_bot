-- Create tables for Italian sentences and phrases
CREATE TABLE IF NOT EXISTS italian_sentences (
    id SERIAL PRIMARY KEY,
    sentence TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS encouraging_phrases (
    id SERIAL PRIMARY KEY,
    phrase TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS error_phrases (
    id SERIAL PRIMARY KEY,
    phrase TEXT NOT NULL
);

-- Create migrations tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial Italian sentences
INSERT INTO italian_sentences (sentence) VALUES
    ('Ciao come stai'),
    ('Buongiorno a tutti'),
    ('Mi piace la pizza'),
    ('Mi chiamo Luca e studio italiano'),
    ('Parlo un po'' di italiano'),
    ('Buongiorno, come stai oggi?'),
    ('Che bel tempo'),
    ('Mi piace l''italiano'),
    ('Vorrei ordinare una pizza margherita'),
    ('Dove si trova la stazione?'),
    ('Posso avere un caffè, per favore?'),
    ('Quanto costa questo libro?'),
    ('Amo il caffè italiano ogni mattina.'),
    ('In Italia il sole splende sempre.'),
    ('Come si dice "please" in italiano?'),
    ('Domani andiamo al mercato insieme.'),
    ('La pasta al pomodoro è deliziosa.');

-- Insert initial encouraging phrases
INSERT INTO encouraging_phrases (phrase) VALUES
    ('Bravo!'),
    ('Perfetto!'),
    ('Esatto!'),
    ('Bravissimo!'),
    ('Ottimo lavoro!'),
    ('Ben fatto!'),
    ('Complimenti!'),
    ('Sei fortissimo!'),
    ('Continua così!'),
    ('Fantastico!'),
    ('Eccellente risposta!'),
    ('Proprio giusto!'),
    ('Sei un campione!'),
    ('Grandioso!'),
    ('Impari in fretta!'),
    ('Ma dai, sei troppo bravo!'),
    ('Non ci credo, risposta perfetta!'),
    ('Wow, livello madrelingua!'),
    ('Sei il mio studente migliore!');

-- Insert initial error phrases
INSERT INTO error_phrases (phrase) VALUES
    ('Quasi! Ci sei andato vicinissimo.'),
    ('Non proprio, ma ci sei quasi!'),
    ('Piccolo errore, proviamo ancora?'),
    ('Non preoccuparti, è un errore comune.'),
    ('Oops! La risposta giusta è…'),
    ('Tranquillo, capita a tutti.'),
    ('Errore normale.'),
    ('Non è esatto, ma stai imparando!'),
    ('Dai, riproviamo: sono sicuro che ora ci arrivi!'),
    ('Sbagliato di poco, bravissimo lo stesso!'),
    ('Nessun problema, gli errori aiutano a imparare.'),
    ('Non era questa, ma sei sulla strada giusta!'),
    ('Coraggio, un altro tentativo e ce la fai!'),
    ('Macché! Però mi piace che ci provi.'),
    ('Peccato, era così vicina la risposta giusta!');