CREATE DATABASE IF NOT EXISTS drug_interaction;
use drug_interaction;
 SELECT COUNT(*) FROM products; 
 
 SELECT * FROM drug_interaction.drug_events ORDER BY created_at DESC;

SELECT * FROM drug_interaction.interaction_results;

SELECT * FROM drug_interaction.products LIMIT 50;

SELECT drug_a, drug_b, severity, confidence, explanation, created_at 
FROM drug_interaction.interaction_results 
ORDER BY created_at DESC;

SELECT drug_a, COUNT(*) as search_count 
FROM drug_interaction.drug_events 
GROUP BY drug_a 
ORDER BY search_count DESC;


SELECT product_name, medicine_desc, side_effects, drug_interactions 
FROM drug_interaction.products 
WHERE product_name LIKE '%Aspirin%';

SELECT drug_a, drug_b, severity, JSON_EXTRACT(text, '$') 
FROM drug_interaction.rag_documents 
LIMIT 20;

SELECT * FROM drug_interaction.drug_events 
WHERE drug_a = 'Lisinopril' OR drug_b = 'Lisinopril'
ORDER BY created_at DESC;
