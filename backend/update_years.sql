-- Update student annee_courante to distribute students across years
-- This script will distribute 12 students: 4 in Year 1, 4 in Year 2, 4 in Year 3

-- First, let's see the current distribution
SELECT annee_courante, COUNT(*) as count 
FROM etudiants 
WHERE promotion_id = 'a6156fc0-a52a-45aa-bb10-e95a0e258d8e' AND is_active = true
GROUP BY annee_courante
ORDER BY annee_courante;

-- Update students to distribute them across years
-- Students 1-4: Year 1
UPDATE etudiants 
SET annee_courante = 1 
WHERE id IN (
    SELECT id FROM etudiants 
    WHERE promotion_id = 'a6156fc0-a52a-45aa-bb10-e95a0e258d8e' AND is_active = true
    ORDER BY nom, prenom
    LIMIT 4
);

-- Students 5-8: Year 2  
UPDATE etudiants 
SET annee_courante = 2 
WHERE id IN (
    SELECT id FROM etudiants 
    WHERE promotion_id = 'a6156fc0-a52a-45aa-bb10-e95a0e258d8e' AND is_active = true
    ORDER BY nom, prenom
    LIMIT 4 OFFSET 4
);

-- Students 9-12: Year 3
UPDATE etudiants 
SET annee_courante = 3 
WHERE id IN (
    SELECT id FROM etudiants 
    WHERE promotion_id = 'a6156fc0-a52a-45aa-bb10-e95a0e258d8e' AND is_active = true
    ORDER BY nom, prenom
    LIMIT 4 OFFSET 8
);

-- Verify the new distribution
SELECT annee_courante, COUNT(*) as count 
FROM etudiants 
WHERE promotion_id = 'a6156fc0-a52a-45aa-bb10-e95a0e258d8e' AND is_active = true
GROUP BY annee_courante
ORDER BY annee_courante;

-- Show the final student distribution
SELECT nom, prenom, annee_courante 
FROM etudiants 
WHERE promotion_id = 'a6156fc0-a52a-45aa-bb10-e95a0e258d8e' AND is_active = true
ORDER BY annee_courante, nom, prenom; 