CREATE TABLE topics (
    title VARCHAR(255) PRIMARY KEY
);

CREATE TABLE customers (
    name VARCHAR(255) PRIMARY KEY,
    score INT
);

CREATE TABLE feature_requests (
    title VARCHAR(255),
    customer_name VARCHAR(255),
    description VARCHAR(1000) PRIMARY KEY,
    time TIMESTAMP,
    FOREIGN KEY (title) REFERENCES topics(title),
    FOREIGN KEY (customer_name) REFERENCES customers(name)
);


INSERT INTO customers (name, score) VALUES ('Nylas', 4);
INSERT INTO customers (name, score) VALUES ('SPORTSBET', 4);
INSERT INTO customers (name, score) VALUES ('Broadcom', 4);
INSERT INTO customers (name, score) VALUES ('LifeLabs', 4);
INSERT INTO customers (name, score) VALUES ('BitSight Technologies Inc', 4);
INSERT INTO customers (name, score) VALUES ('FanDuel Inc', 4);
INSERT INTO customers (name, score) VALUES ('Hudson River Trading', 4);
INSERT INTO customers (name, score) VALUES ('"Coinbase, Inc."', 4);
INSERT INTO customers (name, score) VALUES ('GUIDEWIRE', 4);
INSERT INTO customers (name, score) VALUES ('Snowflake', 4);
INSERT INTO customers (name, score) VALUES ('Transocean (Deepwater)', 3);
INSERT INTO customers (name, score) VALUES ('Canada Infrastructure Bank', 3);
INSERT INTO customers (name, score) VALUES ('Convera', 3);
INSERT INTO customers (name, score) VALUES ('PayNearMe', 3);
INSERT INTO customers (name, score) VALUES ('OneMain Financial', 3);
INSERT INTO customers (name, score) VALUES ('Verily', 3);
INSERT INTO customers (name, score) VALUES ('Apex Fintech Solutions', 3);
INSERT INTO customers (name, score) VALUES ('Elastic', 3);
INSERT INTO customers (name, score) VALUES ('Compass', 3);
INSERT INTO customers (name, score) VALUES ('Coveo', 3);
INSERT INTO customers (name, score) VALUES ('Benchling', 3);
INSERT INTO customers (name, score) VALUES ('Avant LLC', 3);
INSERT INTO customers (name, score) VALUES ('Hinge', 3);
INSERT INTO customers (name, score) VALUES ('SoFi', 3);
INSERT INTO customers (name, score) VALUES ('Fireblocks', 3);
INSERT INTO customers (name, score) VALUES ('aPriori', 3);
INSERT INTO customers (name, score) VALUES ('Sourcegraph', 3);
INSERT INTO customers (name, score) VALUES ('North American Bancard', 3);
INSERT INTO customers (name, score) VALUES ('Grafana', 3);
INSERT INTO customers (name, score) VALUES ('Plaid', 3);
INSERT INTO customers (name, score) VALUES ('Navan (Tripactions)', 3);
INSERT INTO customers (name, score) VALUES ('JFrog Ltd', 3);
INSERT INTO customers (name, score) VALUES ('3Commas', 2);
INSERT INTO customers (name, score) VALUES ('Avetta', 2);
INSERT INTO customers (name, score) VALUES ('ThetaRay', 2);
INSERT INTO customers (name, score) VALUES ('EPAM Corp', 2);
INSERT INTO customers (name, score) VALUES ('Cricut', 2);
INSERT INTO customers (name, score) VALUES ('ARISTOCRAT LEISURE LIMITED', 2);
INSERT INTO customers (name, score) VALUES ('Noname Security', 2);
INSERT INTO customers (name, score) VALUES ('CS Disco', 2);
INSERT INTO customers (name, score) VALUES ('Apptio', 2);
INSERT INTO customers (name, score) VALUES ('Swimlane', 2);
INSERT INTO customers (name, score) VALUES ('Docker', 2);
INSERT INTO customers (name, score) VALUES ('OpenSesame', 2);
INSERT INTO customers (name, score) VALUES ('BigID', 2);
INSERT INTO customers (name, score) VALUES ('Moveworks', 2);
INSERT INTO customers (name, score) VALUES ('Codat', 2);
INSERT INTO customers (name, score) VALUES ('Collibra Inc.', 2);
INSERT INTO customers (name, score) VALUES ('Egress', 2);
INSERT INTO customers (name, score) VALUES ('Seemplicity', 2);
INSERT INTO customers (name, score) VALUES ('Torq', 2);
INSERT INTO customers (name, score) VALUES ('SiteRx', 2);
INSERT INTO customers (name, score) VALUES ('Big Fish Games', 2);
INSERT INTO customers (name, score) VALUES ('Kvika banki hf', 2);
INSERT INTO customers (name, score) VALUES ('Adenza', 2);
INSERT INTO customers (name, score) VALUES ('Unit', 2);
INSERT INTO customers (name, score) VALUES ('Thumbtack', 2);
INSERT INTO customers (name, score) VALUES ('Cantaloupe', 2);
INSERT INTO customers (name, score) VALUES ('Whistic', 2);
INSERT INTO customers (name, score) VALUES ('"Age of Learning, Inc."', 2);
INSERT INTO customers (name, score) VALUES ('Amplitude', 2);
INSERT INTO customers (name, score) VALUES ('Operative', 2);
INSERT INTO customers (name, score) VALUES ('Global-e', 2);
INSERT INTO customers (name, score) VALUES ('Tipalti', 2);
INSERT INTO customers (name, score) VALUES ('accessiBe', 2);
INSERT INTO customers (name, score) VALUES ('View The Space', 2);
INSERT INTO customers (name, score) VALUES ('Cyera', 2);
INSERT INTO customers (name, score) VALUES ('Jellyvision Lab Inc.', 2);
INSERT INTO customers (name, score) VALUES ('ServiceTitan', 2);
INSERT INTO customers (name, score) VALUES ('Schrodinger', 2);
INSERT INTO customers (name, score) VALUES ('Axonius', 2);
INSERT INTO customers (name, score) VALUES ('DoiT International Ltd', 2);
INSERT INTO customers (name, score) VALUES ('Varonis Systems Inc', 2);
INSERT INTO customers (name, score) VALUES ('New American Funding', 2);
INSERT INTO customers (name, score) VALUES ('Riskified', 2);
INSERT INTO customers (name, score) VALUES ('Neoway', 1);
INSERT INTO customers (name, score) VALUES ('Charlie', 1);
INSERT INTO customers (name, score) VALUES ('Smartwatcher Security Services Ltd.', 1);
INSERT INTO customers (name, score) VALUES ('Finfare', 1);
INSERT INTO customers (name, score) VALUES ('Microblink', 1);
INSERT INTO customers (name, score) VALUES ('PetalMD', 1);
INSERT INTO customers (name, score) VALUES ('BDC', 1);
INSERT INTO customers (name, score) VALUES ('Sightful (Prev Multinarity)', 1);
INSERT INTO customers (name, score) VALUES ('KPA', 1);
INSERT INTO customers (name, score) VALUES ('LiveU', 1);
INSERT INTO customers (name, score) VALUES ('Wrapbook', 1);
INSERT INTO customers (name, score) VALUES ('Armis', 1);
INSERT INTO customers (name, score) VALUES ('Cloudinary', 1);
INSERT INTO customers (name, score) VALUES ('CardinalOps', 1);
INSERT INTO customers (name, score) VALUES ('OpenWeb', 1);
INSERT INTO customers (name, score) VALUES ('Minute Media', 1);
INSERT INTO customers (name, score) VALUES ('Hyro', 1);
INSERT INTO customers (name, score) VALUES ('Snappy', 1);
INSERT INTO customers (name, score) VALUES ('Infomedia Inc.', 1);
INSERT INTO customers (name, score) VALUES ('Funnel.io', 1);
INSERT INTO customers (name, score) VALUES ('Silverfort', 1);
INSERT INTO customers (name, score) VALUES ('Atera', 1);
INSERT INTO customers (name, score) VALUES ('Hunters', 1);
INSERT INTO customers (name, score) VALUES ('Zenity', 1);
INSERT INTO customers (name, score) VALUES ('Melio Payments', 1);
INSERT INTO customers (name, score) VALUES ('Sygnia', 1);
INSERT INTO customers (name, score) VALUES ('Earnix', 1);
INSERT INTO customers (name, score) VALUES ('HiBob', 1);
INSERT INTO customers (name, score) VALUES ('ControlUp', 1);
INSERT INTO customers (name, score) VALUES ('StableLogic', 1);
INSERT INTO customers (name, score) VALUES ('Live Metric', 1);
INSERT INTO customers (name, score) VALUES ('Copyleaks', 1);


DELETE FROM topics;
select * from topics;

delete from feature_requests ;
select * from feature_requests fr ;

