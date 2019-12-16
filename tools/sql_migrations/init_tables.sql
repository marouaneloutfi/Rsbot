CREATE TABLE IF NOT EXISTS models
(
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    description   TEXT,
    input_shape   TEXT NOT NULL,
    classes       TEXT NOT NULL,
    palette       TEXT,
    date_created  TEXT,
    date_modified TEXT
);


CREATE TABLE IF NOT EXISTS results
(
    id             INTEGER PRIMARY KEY,
    status         TEXT NOT NULL,
    train_loss     REAL,
    val_loss       REAL,
    train_accuracy REAL,
    val_accuracy   REAL,
    experiment_id  INTEGER,
    FOREIGN KEY (experiment_id) REFERENCES experiments (id)
);

CREATE TABLE IF NOT EXISTS experiments
(

    id            INTEGER PRIMARY KEY,
    train_size    INTEGER,
    val_size      INTEGER,
    epochs        INTEGER,
    batch_size    INTEGER,
    loss_function TEXT,
    training_time REAL,
    save_location TEXT    NOT NULL,
    model_id      INTEGER NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models (id)
);
