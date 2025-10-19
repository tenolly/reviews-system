-- TEACHERS
INSERT INTO teachers (isu, name) SELECT 1001, 'Смирнов А.А.'
WHERE NOT EXISTS (SELECT 1 FROM teachers WHERE isu=1001);
INSERT INTO teachers (isu, name) SELECT 1002, 'Иванова И.И.'
WHERE NOT EXISTS (SELECT 1 FROM teachers WHERE isu=1002);
INSERT INTO teachers (isu, name) SELECT 1003, 'Петров П.П.'
WHERE NOT EXISTS (SELECT 1 FROM teachers WHERE isu=1003);

-- SUBJECTS
INSERT INTO subjects (name) SELECT 'Математический анализ'
WHERE NOT EXISTS (SELECT 1 FROM subjects WHERE name='Математический анализ');
INSERT INTO subjects (name) SELECT 'Линейная алгебра'
WHERE NOT EXISTS (SELECT 1 FROM subjects WHERE name='Линейная алгебра');
INSERT INTO subjects (name) SELECT 'Программирование'
WHERE NOT EXISTS (SELECT 1 FROM subjects WHERE name='Программирование');

-- TAGS
INSERT INTO tags (name) VALUES ('бутерброд')     ON CONFLICT DO NOTHING;
INSERT INTO tags (name) VALUES ('чилл')          ON CONFLICT DO NOTHING;
INSERT INTO tags (name) VALUES ('кринж')         ON CONFLICT DO NOTHING;
INSERT INTO tags (name) VALUES ('много домашки') ON CONFLICT DO NOTHING;
INSERT INTO tags (name) VALUES ('строгий')       ON CONFLICT DO NOTHING;
INSERT INTO tags (name) VALUES ('интересный')    ON CONFLICT DO NOTHING;
INSERT INTO tags (name) VALUES ('харизматичный') ON CONFLICT DO NOTHING;

-- TEACHER_SUBJECTS (M:N)
INSERT INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id FROM teachers t, subjects s
WHERE t.isu=1001 AND s.name='Математический анализ'
ON CONFLICT DO NOTHING;

INSERT INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id FROM teachers t, subjects s
WHERE t.isu=1001 AND s.name='Линейная алгебра'
ON CONFLICT DO NOTHING;

INSERT INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id FROM teachers t, subjects s
WHERE t.isu=1002 AND s.name='Линейная алгебра'
ON CONFLICT DO NOTHING;

INSERT INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id FROM teachers t, subjects s
WHERE t.isu=1002 AND s.name='Программирование'
ON CONFLICT DO NOTHING;

INSERT INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id FROM teachers t, subjects s
WHERE t.isu=1003 AND s.name='Программирование'
ON CONFLICT DO NOTHING;

-- REVIEWS
INSERT INTO reviews
(teacher_id, subject_id, study_year, comment, overall, difficulty, interesting, organization, fairness)
SELECT
  (SELECT id FROM teachers  WHERE isu=1001),
  (SELECT id FROM subjects  WHERE name='Математический анализ'),
  2024, 'Сильная подача, тяжело, но полезно.', 5,5,4,5,5
WHERE EXISTS (
  SELECT 1 FROM teacher_subjects
  WHERE teacher_id=(SELECT id FROM teachers WHERE isu=1001)
    AND subject_id=(SELECT id FROM subjects WHERE name='Математический анализ')
)
AND NOT EXISTS (
  SELECT 1 FROM reviews
  WHERE teacher_id=(SELECT id FROM teachers WHERE isu=1001)
    AND subject_id=(SELECT id FROM subjects WHERE name='Математический анализ')
    AND comment='Сильная подача, тяжело, но полезно.'
);

INSERT INTO reviews
(teacher_id, subject_id, study_year, comment, overall, difficulty, interesting, organization, fairness)
SELECT
  (SELECT id FROM teachers  WHERE isu=1002),
  (SELECT id FROM subjects  WHERE name='Программирование'),
  2023, 'Практики много, материал современный.', 4,3,5,4,4
WHERE EXISTS (
  SELECT 1 FROM teacher_subjects
  WHERE teacher_id=(SELECT id FROM teachers WHERE isu=1002)
    AND subject_id=(SELECT id FROM subjects WHERE name='Программирование')
)
AND NOT EXISTS (
  SELECT 1 FROM reviews
  WHERE teacher_id=(SELECT id FROM teachers WHERE isu=1002)
    AND subject_id=(SELECT id FROM subjects WHERE name='Программирование')
    AND comment='Практики много, материал современный.'
);

INSERT INTO reviews
(teacher_id, subject_id, study_year, comment, overall, difficulty, interesting, organization, fairness)
SELECT
  (SELECT id FROM teachers  WHERE isu=1001),
  (SELECT id FROM subjects  WHERE name='Линейная алгебра'),
  2025, 'Хорошие конспекты, но строгие дедлайны.', 4,4,4,5,4
WHERE EXISTS (
  SELECT 1 FROM teacher_subjects
  WHERE teacher_id=(SELECT id FROM teachers WHERE isu=1001)
    AND subject_id=(SELECT id FROM subjects WHERE name='Линейная алгебра')
)
AND NOT EXISTS (
  SELECT 1 FROM reviews
  WHERE teacher_id=(SELECT id FROM teachers WHERE isu=1001)
    AND subject_id=(SELECT id FROM subjects WHERE name='Линейная алгебра')
    AND comment='Хорошие конспекты, но строгие дедлайны.'
);

-- REVIEW_TAGS
INSERT INTO review_tags (review_id, tag_id)
SELECT r.id, t.id
FROM reviews r, tags t
WHERE r.comment='Сильная подача, тяжело, но полезно.' AND t.name IN ('строгий','интересный')
ON CONFLICT DO NOTHING;

INSERT INTO review_tags (review_id, tag_id)
SELECT r.id, t.id
FROM reviews r, tags t
WHERE r.comment='Практики много, материал современный.' AND t.name IN ('интересный','харизматичный')
ON CONFLICT DO NOTHING;

INSERT INTO review_tags (review_id, tag_id)
SELECT r.id, t.id
FROM reviews r, tags t
WHERE r.comment='Хорошие конспекты, но строгие дедлайны.' AND t.name IN ('строгий','много домашки')
ON CONFLICT DO NOTHING;

-- USERS
INSERT INTO users (username, password_hash, email, admin)
VALUES
  ('alice', 'hash1', 'alice@example.com', true),
  ('bob',   'hash2', 'bob@example.com',   false)
ON CONFLICT (username) DO NOTHING;

-- FACULTIES
INSERT INTO faculties (code, name) VALUES
  ('ICT', 'Инфокоммуникационные технологии'),
  ('CS',  'Компьютерные технологии и управление')
ON CONFLICT (name) DO NOTHING;

-- TEACHER_FACULTIES
INSERT INTO teacher_faculties (teacher_id, faculty_id, since_date, until_date)
SELECT t.id, f.id, DATE '2022-09-01', NULL
FROM teachers t, faculties f
WHERE t.isu=1001 AND f.code='CS'
ON CONFLICT DO NOTHING;

INSERT INTO teacher_faculties (teacher_id, faculty_id, since_date, until_date)
SELECT t.id, f.id, DATE '2023-09-01', NULL
FROM teachers t, faculties f
WHERE t.isu=1002 AND f.code='ICT'
ON CONFLICT DO NOTHING;

-- TEACHER_PHOTOS
INSERT INTO teacher_photos (teacher_id, url, is_primary, source)
SELECT id, 'https://example.com/p/1001.jpg', true, 'seed'
FROM teachers WHERE isu=1001
ON CONFLICT DO NOTHING;

INSERT INTO teacher_photos (teacher_id, url, is_primary, source)
SELECT id, 'https://example.com/p/1002.jpg', true, 'seed'
FROM teachers WHERE isu=1002
ON CONFLICT DO NOTHING;

-- BLACK_LIST
INSERT INTO black_list (reason, user_id)
SELECT 'спам', u.id FROM users u WHERE u.username='bob'
ON CONFLICT DO NOTHING;

-- MODERATION_ACTIONS (пример на отзыв)
INSERT INTO moderation_actions (target_type, target_id, moderator_id, action, note)
SELECT 'review',
       r.id,
       (SELECT id FROM users WHERE username='alice'),
       'hide',
       'тестовая модерация'
FROM reviews r
WHERE r.comment='кринж-комментарий, которого нет'
AND NOT EXISTS (
  SELECT 1 FROM moderation_actions m
  WHERE m.target_type='review' AND m.target_id=r.id AND m.action='hide'
);
