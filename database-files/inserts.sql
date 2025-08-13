Use BallWatch;

-- Clear existing data to prevent duplicates
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM TeamsPlayers;
DELETE FROM DraftEvaluations;
DELETE FROM PlayerGameStats;
DELETE FROM PlayerMatchup;
DELETE FROM GamePlans;
DELETE FROM Game;
DELETE FROM Players;
DELETE FROM Teams;
DELETE FROM Agent;
DELETE FROM Users;
SET FOREIGN_KEY_CHECKS = 1;

-- Reset auto-increment values
ALTER TABLE Users AUTO_INCREMENT = 1;
ALTER TABLE Agent AUTO_INCREMENT = 1;
ALTER TABLE Teams AUTO_INCREMENT = 1;
ALTER TABLE Players AUTO_INCREMENT = 1;
ALTER TABLE Game AUTO_INCREMENT = 1;
ALTER TABLE DraftEvaluations AUTO_INCREMENT = 1;
ALTER TABLE GamePlans AUTO_INCREMENT = 1;

INSERT INTO Users (email, username, role) VALUES
('mike.lewis@ballwatch.com', 'mlewis', 'admin'),
('marcus.thompson@nets.com', 'mthompson', 'coach'),
('andre.wu@nets.com', 'awu', 'gm'),
('johnny.evans@gmail.com', 'jevans25', 'fan');


INSERT INTO Agent (first_name, last_name, agency_name, phone, email) VALUES
('Rich', 'Paul', 'Klutch Sports Group', '555-0101', 'rich@klutchsports.com'),
('Jeff', 'Schwartz', 'Excel Sports Management', '555-0102', 'jeff@excelsports.com'),
('Mark', 'Bartelstein', 'Priority Sports', '555-0103', 'mark@prioritysports.com');


INSERT INTO Teams (name, conference, division, coach, gm, offensive_system, defensive_system) VALUES
('Brooklyn Nets', 'Eastern', 'Atlantic', 'Marcus Thompson', 'Andre Wu', 'Motion Offense', 'Switch Everything'),
('Los Angeles Lakers', 'Western', 'Pacific', 'Darvin Ham', 'Rob Pelinka', 'LeBron System', 'Drop Coverage'),
('Golden State Warriors', 'Western', 'Pacific', 'Steve Kerr', 'Bob Myers', 'Motion Offense', 'Aggressive Switching'),
('Boston Celtics', 'Eastern', 'Atlantic', 'Joe Mazzulla', 'Brad Stevens', 'Five Out', 'Drop Coverage'),
('Miami Heat', 'Eastern', 'Southeast', 'Erik Spoelstra', 'Pat Riley', 'Zone Attack', 'Zone Defense');


INSERT INTO Players (first_name, last_name, age, college, position, weight, player_status, agent_id,
                   height, DOB, years_exp, dominant_hand, expected_salary, player_type, current_salary, draft_year) VALUES
('Kevin', 'Durant', 35, 'Texas', 'SF', 240, 'Active', 1, '6-10', '1988-09-29', 16, 'Right',
51000000, 'Superstar', 47649433, 2007),
('Kyrie', 'Irving', 32, 'Duke', 'PG', 195, 'Active', 2, '6-2', '1992-03-23', 13, 'Right',
42000000, 'All-Star', 37037037, 2011),
('Ben', 'Simmons', 28, 'LSU', 'PF', 240, 'Active', 1, '6-10', '1996-07-20', 8, 'Left',
40000000, 'All-Star', 37893408, 2016),
('LeBron', 'James', 39, NULL, 'SF', 250, 'Active', 1, '6-9', '1984-12-30', 21, 'Right',
51000000, 'Superstar', 47607350, 2003),
('Stephen', 'Curry', 36, 'Davidson', 'PG', 185, 'Active', 2, '6-2', '1988-03-14', 15, 'Right',
55000000, 'Superstar', 51915615, 2009),
('Cooper', 'Flagg', 18, 'Duke', 'SF', 200, 'Active', 3, '6-9', '2006-12-21', 0, 'Right',
10000000, 'Rookie', 0, 2025),
('Jayson', 'Tatum', 26, 'Duke', 'SF', 210, 'Active', 2, '6-8', '1998-03-03', 7, 'Right',
35000000, 'All-Star', 32600060, 2017),
('Jimmy', 'Butler', 34, 'Marquette', 'SF', 230, 'Active', 1, '6-7', '1989-09-14', 13, 'Right',
48000000, 'All-Star', 48798677, 2011);


INSERT INTO TeamsPlayers (player_id, team_id, joined_date, jersey_num) VALUES
(1, 1, '2023-02-09', 7),
(2, 1, '2023-02-06', 11),
(3, 1, '2022-02-10', 10),
(4, 2, '2018-07-01', 23),
(5, 3, '2009-06-25', 30),
(7, 4, '2017-06-22', 0),
(8, 5, '2019-07-06', 22);


INSERT INTO Game (game_date, season, game_type, home_team_id, away_team_id, home_score, away_score) VALUES
('2025-01-15', '2024-25', 'regular', 1, 2, 118, 112),
('2025-01-18', '2024-25', 'regular', 3, 1, 125, 120),
('2025-01-20', '2024-25', 'regular', 1, 3, 108, 115),
('2025-01-22', '2024-25', 'regular', 4, 5, 122, 118),
('2025-01-25', '2024-25', 'regular', 1, 4, 110, 105);


INSERT INTO LineupConfiguration (team_id, quarter, time_on, time_off, plus_minus, offensive_rating, defensive_rating) VALUES
(1, 1, '12:00:00', '06:00:00', 8, 118.5, 105.2),
(1, 2, '12:00:00', '05:30:00', -3, 102.3, 108.7),
(3, 1, '12:00:00', '07:00:00', 5, 115.2, 110.1),
(2, 1, '12:00:00', '06:30:00', 6, 112.5, 108.3);


INSERT INTO PlayerGameStats (player_id, game_id, points, rebounds, assists, shooting_percentage,
                           plus_minus, minutes_played, turnovers, steals, blocks) VALUES
(1, 1, 35, 8, 5, 0.58, 12, 38, 3, 1, 2),
(2, 1, 28, 4, 8, 0.52, 8, 36, 4, 2, 0),
(3, 1, 12, 6, 4, 0.33, 6, 24, 2, 0, 1),
(4, 1, 32, 10, 7, 0.55, -6, 37, 5, 1, 1),
(1, 2, 30, 6, 4, 0.48, -5, 35, 2, 0, 1),
(5, 2, 38, 5, 11, 0.62, 5, 36, 3, 3, 0),
(1, 3, 27, 9, 3, 0.45, -7, 34, 4, 1, 2),
(5, 3, 42, 4, 9, 0.68, 7, 38, 2, 2, 0);


INSERT INTO PlayerMatchup (game_id, offensive_player_id, defensive_player_id, offensive_rating, defensive_rating,
                         possessions, points_scored, shooting_percentage) VALUES
(1, 1, 4, 125.5, 98.3, 15, 18, 0.60),
(1, 4, 1, 118.2, 102.5, 12, 14, 0.54),
(2, 5, 2, 132.1, 95.2, 18, 22, 0.65),
(3, 1, 5, 108.5, 112.3, 16, 12, 0.40);

INSERT INTO DraftEvaluations (player_id, overall_rating, offensive_rating, defensive_rating, athleticism_rating, potential_rating, evaluation_type, strengths, weaknesses, scout_notes, projected_round, comparison_player) VALUES
(1, 85.5, 82.0, 88.0, 90.0, 92.0, 'free_agent', 'Elite scorer with incredible range', 'Can be inconsistent on defense', 'Future Hall of Famer still playing at elite level', 1, 'Larry Bird'),
(2, 78.0, 85.0, 72.0, 75.0, 80.0, 'free_agent', 'Excellent ball handling and clutch gene', 'Can be a defensive liability', 'Elite offensive player when healthy', 1, 'Allen Iverson'),
(4, 82.0, 75.0, 90.0, 85.0, 78.0, 'free_agent', 'Best shooter of all time', 'Sometimes struggles with size', 'Revolutionary player who changed the game', 1, 'Ray Allen');


INSERT INTO GamePlans (team_id, opponent_id, game_id, plan_name, offensive_strategy, defensive_strategy, special_instructions) VALUES
(1, 3, 3, 'Warriors Game Plan', 'Attack Curry in pick and roll. Post up KD against smaller defenders.',
   'Switch 1-4, drop big on Curry PnR. Force others to beat us.',
   'Double Curry on all side PnRs in clutch time.'),
(1, 4, 5, 'Celtics Game Plan', 'Run through KD in the post. Push pace in transition.',
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


INSERT INTO DataLoads (load_type, status, started_at, completed_at, records_processed, records_failed, initiated_by, source_file) VALUES
('NBA_API', 'completed', '2025-01-20 02:00:00', '2025-01-20 02:15:30', 1250, 0, 'system', 'nba_daily_feed.json'),
('ESPN_Feed', 'completed', '2025-01-21 02:00:00', '2025-01-21 02:12:45', 980, 5, 'system', 'espn_stats.csv'),
('NBA_API', 'failed', '2025-01-22 02:00:00', '2025-01-22 02:05:15', 0, 500, 'system', 'nba_daily_feed.json'),
('Stats_API', 'completed', '2025-01-23 02:00:00', '2025-01-23 02:18:22', 1150, 8, 'system', 'advanced_stats.json'),
('NBA_API', 'completed', '2025-01-24 02:00:00', '2025-01-24 02:14:55', 1300, 2, 'system', 'nba_daily_feed.json');


INSERT INTO ErrorLogs (error_type, severity, module, error_message, user_id) VALUES
('DataQuality', 'warning', 'DataValidation', 'Found 3 players with shooting percentage > 1.0', 1),
('APITimeout', 'error', 'DataIngestion', 'NBA API request timeout after 30 seconds', 1),
('DatabaseConnection', 'critical', 'SystemHealth', 'Lost connection to replica database', NULL),
('DataIntegrity', 'error', 'DataValidation', 'Duplicate game entries detected', 1),
('MemoryLimit', 'warning', 'CacheLayer', 'Cache memory limit exceeded', NULL);


INSERT INTO DataErrors (error_type, table_name, record_id, field_name, invalid_value, expected_format) VALUES
('invalid', 'PlayerGameStats', '123', 'shooting_percentage', '1.25', 'Decimal between 0 and 1'),
('duplicate', 'Game', '456', 'game_id', '456', 'Unique identifier'),
('missing', 'Players', '789', 'position', NULL, 'Required enum value');