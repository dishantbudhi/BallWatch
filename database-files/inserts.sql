INSERT INTO Users (email, username, role) VALUES
('mike.lewis@ballwatch.com', 'mlewis', 'admin'),
('marcus.thompson@nets.com', 'mthompson', 'coach'),
('andre.wu@nets.com', 'awu', 'gm'),
('johnny.evans@gmail.com', 'jevans25', 'fan');


INSERT INTO Agent (first_name, last_name, agency_name, phone, email) VALUES
('Rich', 'Paul', 'Klutch Sports Group', '555-0101', 'rich@klutchsports.com'),
('Jeff', 'Schwartz', 'Excel Sports Management', '555-0102', 'jeff@excelsports.com'),
('Mark', 'Bartelstein', 'Priority Sports', '555-0103', 'mark@prioritysports.com');


INSERT INTO Teams (name, conference, abrv, division, head_coach, offensive_system, defensive_system) VALUES
('Brooklyn Nets', 'Eastern', 'BKN', 'Atlantic', 'Marcus Thompson', 'Motion Offense', 'Switch Everything'),
('Los Angeles Lakers', 'Western', 'LAL', 'Pacific', 'Darvin Ham', 'LeBron System', 'Drop Coverage'),
('Golden State Warriors', 'Western', 'GSW', 'Pacific', 'Steve Kerr', 'Motion Offense', 'Aggressive Switching'),
('Boston Celtics', 'Eastern', 'BOS', 'Atlantic', 'Joe Mazzulla', 'Five Out', 'Drop Coverage'),
('Miami Heat', 'Eastern', 'MIA', 'Southeast', 'Erik Spoelstra', 'Zone Attack', 'Zone Defense');


INSERT INTO Players (first_name, last_name, age, college, position, weight, player_status, agent_id,
                   height, DOB, years_exp, dominant_hand, expected_salary, player_type, current_salary, draft_year) VALUES
('Kevin', 'Durant', 35, 'Texas', 'Forward', 240, 'Active', 1, '6-10', '1988-09-29', 16, 'Right',
51000000, 'Superstar', 47649433, 2007),
('Kyrie', 'Irving', 32, 'Duke', 'Guard', 195, 'Active', 2, '6-2', '1992-03-23', 13, 'Right',
42000000, 'All-Star', 37037037, 2011),
('Ben', 'Simmons', 28, 'LSU', 'Forward', 240, 'Active', 1, '6-10', '1996-07-20', 8, 'Left',
40000000, 'All-Star', 37893408, 2016),
('LeBron', 'James', 39, 'None', 'Forward', 250, 'Active', 1, '6-9', '1984-12-30', 21, 'Right',
51000000, 'Superstar', 47607350, 2003),
('Stephen', 'Curry', 36, 'Davidson', 'Guard', 185, 'Active', 2, '6-2', '1988-03-14', 15, 'Right',
55000000, 'Superstar', 51915615, 2009),
('Cooper', 'Flagg', 18, 'Duke', 'Forward', 200, 'Active', 3, '6-9', '2006-12-21', 0, 'Right',
10000000, 'Rookie', 0, 2025),
('Jayson', 'Tatum', 26, 'Duke', 'Forward', 210, 'Active', 2, '6-8', '1998-03-03', 7, 'Right',
35000000, 'All-Star', 32600060, 2017),
('Jimmy', 'Butler', 34, 'Marquette', 'Forward', 230, 'Active', 1, '6-7', '1989-09-14', 13, 'Right',
48000000, 'All-Star', 48798677, 2011);


INSERT INTO TeamsPlayers (player_id, team_id, joined_date, jersey_num) VALUES
(1, 1, '2023-02-09', 7),
(2, 1, '2023-02-06', 11),
(3, 1, '2022-02-10', 10),
(4, 2, '2018-07-01', 23),
(5, 3, '2009-06-25', 30),
(7, 4, '2017-06-22', 0),
(8, 5, '2019-07-06', 22);


INSERT INTO Game (date, season, is_playoff, home_team_id, away_team_id, home_score, away_score) VALUES
('2025-01-15', '2024-25', FALSE, 1, 2, 118, 112),
('2025-01-18', '2024-25', FALSE, 3, 1, 125, 120),
('2025-01-20', '2024-25', FALSE, 1, 3, 108, 115),
('2025-01-22', '2024-25', FALSE, 4, 5, 122, 118),
('2025-01-25', '2024-25', FALSE, 1, 4, 110, 105);


INSERT INTO LineupConfiguration (team_id, quarter, time_on, time_off, plus_minus, offensive_rating, defensive_rating) VALUES
(1, 1, '12:00:00', '06:00:00', 8, 118.5, 105.2),
(1, 2, '12:00:00', '05:30:00', -3, 102.3, 108.7),
(3, 1, '12:00:00', '07:00:00', 5, 115.2, 110.1),
(2, 1, '12:00:00', '06:30:00', 6, 112.5, 108.3);


INSERT INTO PlayerGameStats (player_id, game_id, team_id, points, rebounds, assists, shooting_percentage,
                           plus_minus, minutes_played, turnovers, steals, blocks, fouls_committed) VALUES
(1, 1, 1, 35, 8, 5, 0.58, 12, 38, 3, 1, 2, 2),
(2, 1, 1, 28, 4, 8, 0.52, 8, 36, 4, 2, 0, 3),
(3, 1, 1, 12, 6, 4, 0.33, 6, 24, 2, 0, 1, 4),
(4, 1, 2, 32, 10, 7, 0.55, -6, 37, 5, 1, 1, 2),
(1, 2, 1, 30, 6, 4, 0.48, -5, 35, 2, 0, 1, 3),
(5, 2, 3, 38, 5, 11, 0.62, 5, 36, 3, 3, 0, 2),
(1, 3, 1, 27, 9, 3, 0.45, -7, 34, 4, 1, 2, 2),
(5, 3, 3, 42, 4, 9, 0.68, 7, 38, 2, 2, 0, 1);


INSERT INTO PlayerMatchup (game_id, offensive_player_id, defensive_player_id, offensive_rating, defensive_rating,
                         possessions, points_scored, shooting_percentage) VALUES
(1, 1, 4, 125.5, 98.3, 15, 18, 0.60),
(1, 4, 1, 118.2, 102.5, 12, 14, 0.54),
(2, 5, 2, 132.1, 95.2, 18, 22, 0.65),
(3, 1, 5, 108.5, 112.3, 16, 12, 0.40);


INSERT INTO DraftEval (player_id, team_id, ranking, notes, nba_player_comparison) VALUES
(6, 1, 1, 'Elite two-way player with high basketball IQ. Can play multiple positions.', 'Jayson Tatum'),
(6, 2, 1, 'Perfect fit next to LeBron. Elite defender and versatile scorer.', 'Paul George'),
(6, 3, 2, 'Would complement Curry well but concerned about overlap with Wiggins.', 'Scottie Barnes'),
(6, 4, 1, 'Ideal modern wing for our system. High upside.', 'Jaylen Brown'),
(6, 5, 3, 'Great talent but concerned about fit with Butler and Bam.', 'Mikal Bridges');


INSERT INTO GamePlan (game_id, offensive_strategy, defensive_strategy, special_situations) VALUES
(3, 'Attack Curry in pick and roll. Post up KD against smaller defenders.',
   'Switch 1-4, drop big on Curry PnR. Force others to beat us.',
   'Double Curry on all side PnRs in clutch time.'),
(5, 'Run through KD in the post. Push pace in transition.',
   'Pack the paint against Tatum drives. Stay home on shooters.',
   'Hack-a-Simmons if game is close in final 2 minutes.');


INSERT INTO KeyMatchups (matchup_text) VALUES
('KD vs LeBron - Battle of the forwards'),
('Kyrie vs Curry - Elite guard matchup'),
('Simmons vs Draymond - Defensive anchors'),
('Durant vs Tatum - Scoring duel'),
('Kyrie vs Smart - Crafty guard battle');


INSERT INTO SystemHealth (service_name, error_rate_pct, avg_response_time, status) VALUES
('API Gateway', 0.02, 145.5, 'Healthy'),
('Database Cluster', 0.00, 23.2, 'Healthy'),
('Cache Layer', 0.15, 8.5, 'Warning'),
('Load Balancer', 0.01, 12.3, 'Healthy'),
('File Storage', 0.05, 156.7, 'Healthy');


INSERT INTO DataLoads (load_date, data_source, status, start_time, end_time) VALUES
('2025-01-20', 'NBA_API', 'Completed', '2025-01-20 02:00:00', '2025-01-20 02:15:30'),
('2025-01-21', 'ESPN_Feed', 'Completed', '2025-01-21 02:00:00', '2025-01-21 02:12:45'),
('2025-01-22', 'NBA_API', 'Failed', '2025-01-22 02:00:00', '2025-01-22 02:05:15'),
('2025-01-23', 'Stats_API', 'Completed', '2025-01-23 02:00:00', '2025-01-23 02:18:22'),
('2025-01-24', 'NBA_API', 'Completed', '2025-01-24 02:00:00', '2025-01-24 02:14:55');


INSERT INTO ErrorLogs (error_type, error_message, service_component, user_id) VALUES
('DataQuality', 'Found 3 players with shooting percentage > 1.0', 'DataValidation', 1),
('APITimeout', 'NBA API request timeout after 30 seconds', 'DataIngestion', 1),
('DatabaseConnection', 'Lost connection to replica database', 'SystemHealth', NULL),
('DataIntegrity', 'Duplicate game entries detected', 'DataValidation', 1),
('MemoryLimit', 'Cache memory limit exceeded', 'CacheLayer', NULL);


INSERT INTO DataErrors (load_id, error_id) VALUES
(3, 2),
(1, 1),
(3, 3);