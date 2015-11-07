CREATE TABLE "secrets" (
	`id`	TEXT NOT NULL,
	`timestamp`	INTEGER NOT NULL,
	`content`	TEXT NOT NULL,
	`password`	TEXT,
	`access_key`	TEXT NOT NULL,
	PRIMARY KEY(id)
);