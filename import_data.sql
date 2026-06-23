-- Début de l'opération
BEGIN;

-- On vide la table
TRUNCATE TABLE localisation CASCADE;

-- On insère les données (je t'ai mis un exemple, mets tout ton contenu ici)
INSERT INTO localisation (code_departement, nom_departement, nom_region) VALUES
('01', 'Ain', 'Auvergne-Rhône-Alpes'),
('02', 'Aisne', 'Hauts-de-France');

-- On valide tout
COMMIT;