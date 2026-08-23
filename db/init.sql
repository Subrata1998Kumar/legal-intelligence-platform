INSERT INTO users (username, password, role) VALUES
('admin', 'admin', 'Admin'),
('advisor_1', 'advisor_1', 'Senior_Advisor'),
('advisor_2', 'advisor_2', 'Senior_Advisor'),
('advisor_3', 'advisor_3', 'Senior_Advisor'),
('officer_1', 'officer_1', 'Legal_Officer'),
('officer_2', 'officer_2', 'Legal_Officer'),
('clerk_1', 'clerk_1', 'Legal_Officer'),
('officer_3', 'officer_3', 'Legal_Officer'),
('clerk_2', 'clerk_2', 'Legal_Officer'),
('review_1', 'review_1', 'Senior_Advisor')
ON CONFLICT (username) DO NOTHING;
