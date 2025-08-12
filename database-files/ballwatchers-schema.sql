CREATE SCHEMA IF NOT EXISTS BallWatch;
USE BallWatch;

-- Drop tables in correct order (respecting foreign key constraints)
DROP TABLE IF EXISTS ValidationReports;
DROP TABLE IF EXISTS CleanupHistory;
DROP TABLE IF EXISTS CleanupSchedule;
DROP TABLE IF EXISTS DataErrors;
DROP TABLE IF EXISTS ErrorLogs;
DROP TABLE IF EXISTS DataLoads;
DROP TABLE IF EXISTS SystemHealth;
DROP TABLE IF EXISTS GamePlans;
DROP TABLE IF EXISTS KeyMatchups;
DROP TABLE IF EXISTS GamePlayers;
DROP TABLE IF EXISTS PlayerGameStats;
DROP TABLE IF EXISTS PlayerMatchup;
DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS TeamsPlayers;
DROP TABLE IF EXISTS DraftEvaluations;
DROP TABLE IF EXISTS PlayerLineups;
DROP TABLE IF EXISTS Teams;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS LineupConfiguration;
DROP TABLE IF EXISTS Agent;
DROP TABLE IF EXISTS Users;

CREATE TABLE IF NOT EXISTS Users (
   user_id INT PRIMARY KEY AUTO_INCREMENT,
   email VARCHAR(100) UNIQUE NOT NULL,
   username VARCHAR(50) UNIQUE NOT NULL,
   role ENUM('admin', 'coach', 'gm', 'analyst', 'fan') NOT NULL,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS Agent (
   agent_id INT PRIMARY KEY AUTO_INCREMENT,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   agency_name VARCHAR(100),
   phone VARCHAR(20),
   email VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS Players (
   player_id INT PRIMARY KEY AUTO_INCREMENT,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   age INT CHECK (age > 0),
   college VARCHAR(100),
   position ENUM('Guard', 'Forward', 'Center', 'PG', 'SG', 'SF', 'PF', 'C'),
   weight INT CHECK (weight > 0),
   player_status ENUM('Active', 'Injured', 'Retired', 'G-League') DEFAULT 'Active',
   agent_id INT,
   height VARCHAR(10),
   picture TEXT,
   DOB DATE,
   years_exp INT DEFAULT 0,
   dominant_hand ENUM('Left', 'Right') DEFAULT 'Right',
   expected_salary DECIMAL(12,2),
   player_type VARCHAR(50),
   current_salary DECIMAL(12,2),
   draft_year INT,
   CONSTRAINT FK_Players_Agent FOREIGN KEY (agent_id) REFERENCES Agent(agent_id)
       ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Teams (
   team_id INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(100) NOT NULL,
   city VARCHAR(50),
   state VARCHAR(50),
   arena VARCHAR(100),
   conference ENUM('Eastern', 'Western') NOT NULL,
   division VARCHAR(50) NOT NULL,
   coach VARCHAR(100),
   gm VARCHAR(100),
   owner VARCHAR(100),
   championships INT DEFAULT 0,
   founded_year INT,
   offensive_system VARCHAR(100),
   defensive_system VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS TeamsPlayers (
   player_id INT,
   team_id INT,
   joined_date DATE,
   jersey_num INT CHECK (jersey_num BETWEEN 0 AND 99),
   left_date DATE,
   status VARCHAR(50) DEFAULT 'active',
   PRIMARY KEY (player_id, team_id, joined_date),
   CONSTRAINT FK_TeamsPlayers_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_TeamsPlayers_Teams FOREIGN KEY (team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT CHK_Dates CHECK (left_date IS NULL OR left_date >= joined_date)
);

-- Fixed Game table with all required columns
CREATE TABLE IF NOT EXISTS Game (
   game_id INT PRIMARY KEY AUTO_INCREMENT,
   game_date DATE NOT NULL,
   game_time TIME,
   home_team_id INT NOT NULL,
   away_team_id INT NOT NULL,
   home_score INT DEFAULT 0,
   away_score INT DEFAULT 0,
   season VARCHAR(20) NOT NULL,
   game_type ENUM('regular', 'playoff') DEFAULT 'regular',
   status ENUM('scheduled', 'in_progress', 'completed') DEFAULT 'scheduled',
   attendance INT,
   venue VARCHAR(100),
   CONSTRAINT FK_Game_HomeTeam FOREIGN KEY (home_team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT FK_Game_AwayTeam FOREIGN KEY (away_team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Fixed PlayerGameStats with all required columns
CREATE TABLE IF NOT EXISTS PlayerGameStats (
   player_id INT NOT NULL,
   game_id INT NOT NULL,
   points INT DEFAULT 0,
   rebounds INT DEFAULT 0,
   assists INT DEFAULT 0,
   steals INT DEFAULT 0,
   blocks INT DEFAULT 0,
   turnovers INT DEFAULT 0,
   shooting_percentage DECIMAL(5,3),
   three_point_percentage DECIMAL(5,3),
   free_throw_percentage DECIMAL(5,3),
   plus_minus INT DEFAULT 0,
   minutes_played INT DEFAULT 0,
   PRIMARY KEY (player_id, game_id),
   CONSTRAINT FK_PlayerGameStats_Player FOREIGN KEY (player_id) 
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_PlayerGameStats_Game FOREIGN KEY (game_id) 
       REFERENCES Game(game_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS PlayerMatchup (
   game_id INT,
   offensive_player_id INT,
   defensive_player_id INT,
   offensive_rating DECIMAL(5,2),
   defensive_rating DECIMAL(5,2),
   possessions INT,
   points_scored INT,
   shooting_percentage DECIMAL(5,3),
   PRIMARY KEY (game_id, offensive_player_id, defensive_player_id),
   CONSTRAINT FK_PlayerMatchup_Game FOREIGN KEY (game_id)
       REFERENCES Game(game_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_PlayerMatchup_OffensivePlayer FOREIGN KEY (offensive_player_id)
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_PlayerMatchup_DefensivePlayer FOREIGN KEY (defensive_player_id)
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS LineupConfiguration (
   lineup_id INT PRIMARY KEY AUTO_INCREMENT,
   team_id INT NOT NULL,
   quarter INT CHECK (quarter BETWEEN 1 AND 4),
   time_on TIME,
   time_off TIME,
   plus_minus INT,
   offensive_rating DECIMAL(5,2),
   defensive_rating DECIMAL(5,2),
   CONSTRAINT FK_LineupConfiguration_Teams FOREIGN KEY (team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS PlayerLineups (
   player_id INT,
   lineup_id INT,
   position_in_lineup VARCHAR(50),
   PRIMARY KEY (player_id, lineup_id),
   CONSTRAINT FK_PlayerLineups_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_PlayerLineups_LineupConfiguration FOREIGN KEY (lineup_id)
       REFERENCES LineupConfiguration(lineup_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Fixed table name: DraftEvaluations (not DraftEval)
CREATE TABLE IF NOT EXISTS DraftEvaluations (
   evaluation_id INT PRIMARY KEY AUTO_INCREMENT,
   player_id INT NOT NULL,
   overall_rating DECIMAL(5,2) CHECK (overall_rating BETWEEN 0 AND 100),
   offensive_rating DECIMAL(5,2),
   defensive_rating DECIMAL(5,2),
   athleticism_rating DECIMAL(5,2),
   potential_rating DECIMAL(5,2),
   evaluation_type ENUM('prospect', 'free_agent', 'trade_target') DEFAULT 'prospect',
   strengths TEXT,
   weaknesses TEXT,
   scout_notes TEXT,
   projected_round INT,
   comparison_player VARCHAR(100),
   last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   UNIQUE KEY unique_player_evaluation (player_id),
   CONSTRAINT FK_DraftEvaluations_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS KeyMatchups (
   matchup_id INT PRIMARY KEY AUTO_INCREMENT,
   matchup_text TEXT NOT NULL
);

-- Fixed table name: GamePlans (not GamePlan)
CREATE TABLE IF NOT EXISTS GamePlans (
   plan_id INT PRIMARY KEY AUTO_INCREMENT,
   team_id INT NOT NULL,
   opponent_id INT,
   game_id INT,
   plan_name VARCHAR(200) NOT NULL,
   offensive_strategy TEXT,
   defensive_strategy TEXT,
   key_matchups TEXT,
   special_instructions TEXT,
   status ENUM('draft', 'active', 'archived') DEFAULT 'draft',
   created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
   updated_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   CONSTRAINT FK_GamePlans_Team FOREIGN KEY (team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_GamePlans_Opponent FOREIGN KEY (opponent_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_GamePlans_Game FOREIGN KEY (game_id)
       REFERENCES Game(game_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS SystemHealth (
   health_id INT PRIMARY KEY AUTO_INCREMENT,
   check_time DATETIME DEFAULT CURRENT_TIMESTAMP,
   service_name VARCHAR(100) NOT NULL,
   error_rate_pct DECIMAL(5,2),
   avg_response_time DECIMAL(10,2),
   status ENUM('Healthy', 'Warning', 'Error', 'Critical') DEFAULT 'Healthy'
);

CREATE TABLE IF NOT EXISTS ErrorLogs (
   error_id INT PRIMARY KEY AUTO_INCREMENT,
   error_type VARCHAR(100),
   severity ENUM('info', 'warning', 'error', 'critical') NOT NULL,
   module VARCHAR(100),
   error_message TEXT,
   stack_trace TEXT,
   user_id INT,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   resolved_at DATETIME,
   resolved_by VARCHAR(100),
   resolution_notes TEXT,
   CONSTRAINT FK_ErrorLogs_Users FOREIGN KEY (user_id)
       REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS DataLoads (
   load_id INT PRIMARY KEY AUTO_INCREMENT,
   load_type VARCHAR(100),
   status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
   started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   completed_at DATETIME,
   records_processed INT DEFAULT 0,
   records_failed INT DEFAULT 0,
   error_message TEXT,
   initiated_by VARCHAR(100),
   source_file VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS DataErrors (
   data_error_id INT PRIMARY KEY AUTO_INCREMENT,
   error_type ENUM('duplicate', 'missing', 'invalid') NOT NULL,
   table_name VARCHAR(100) NOT NULL,
   record_id VARCHAR(100),
   field_name VARCHAR(100),
   invalid_value TEXT,
   expected_format VARCHAR(255),
   detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   resolved_at DATETIME,
   auto_fixed BOOLEAN DEFAULT FALSE
);

-- Missing tables needed by admin routes
CREATE TABLE IF NOT EXISTS CleanupSchedule (
   schedule_id INT PRIMARY KEY AUTO_INCREMENT,
   cleanup_type VARCHAR(100) NOT NULL,
   frequency ENUM('daily', 'weekly', 'monthly') NOT NULL,
   next_run DATETIME,
   last_run DATETIME,
   retention_days INT NOT NULL,
   is_active BOOLEAN DEFAULT TRUE,
   created_by VARCHAR(100),
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CleanupHistory (
   history_id INT PRIMARY KEY AUTO_INCREMENT,
   schedule_id INT,
   cleanup_type VARCHAR(100),
   started_at DATETIME,
   completed_at DATETIME,
   records_deleted INT,
   status ENUM('started', 'completed', 'failed') DEFAULT 'started',
   error_message TEXT,
   CONSTRAINT FK_CleanupHistory_Schedule FOREIGN KEY (schedule_id)
       REFERENCES CleanupSchedule(schedule_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ValidationReports (
   validation_id INT PRIMARY KEY AUTO_INCREMENT,
   validation_type VARCHAR(100) NOT NULL,
   table_name VARCHAR(100) NOT NULL,
   status ENUM('passed', 'failed', 'warning') NOT NULL,
   total_records INT,
   valid_records INT,
   invalid_records INT,
   validation_rules JSON,
   error_details TEXT,
   run_date DATETIME DEFAULT CURRENT_TIMESTAMP,
   run_by VARCHAR(100)
);

-- Insert sample data
INSERT INTO Users (email, username, role) VALUES
('admin@ballwatch.com', 'admin', 'admin'),
('coach@nets.com', 'coach', 'coach'),
('gm@nets.com', 'gm', 'gm'),
('fan@example.com', 'superfan', 'fan');

INSERT INTO Agent (first_name, last_name, agency_name, phone, email) VALUES
('Rich', 'Paul', 'Klutch Sports', '555-0101', 'rich@klutch.com'),
('Jeff', 'Schwartz', 'Excel Sports', '555-0102', 'jeff@excel.com');

INSERT INTO Teams (name, city, state, arena, conference, division, coach, gm, founded_year) VALUES
('Brooklyn Nets', 'Brooklyn', 'NY', 'Barclays Center', 'Eastern', 'Atlantic', 'Marcus Thompson', 'Andre Wu', 1967),
('Los Angeles Lakers', 'Los Angeles', 'CA', 'Crypto.com Arena', 'Western', 'Pacific', 'Darvin Ham', 'Rob Pelinka', 1947),
('Golden State Warriors', 'San Francisco', 'CA', 'Chase Center', 'Western', 'Pacific', 'Steve Kerr', 'Bob Myers', 1946),
('Boston Celtics', 'Boston', 'MA', 'TD Garden', 'Eastern', 'Atlantic', 'Joe Mazzulla', 'Brad Stevens', 1946);

INSERT INTO Players (first_name, last_name, age, college, position, weight, player_status, agent_id, height, DOB, years_exp, expected_salary, current_salary) VALUES
('Kevin', 'Durant', 35, 'Texas', 'SF', 240, 'Active', 1, '6-10', '1988-09-29', 16, 51000000, 47649433),
('Kyrie', 'Irving', 32, 'Duke', 'PG', 195, 'Active', 2, '6-2', '1992-03-23', 13, 42000000, 37037037),
('LeBron', 'James', 39, NULL, 'SF', 250, 'Active', 1, '6-9', '1984-12-30', 21, 51000000, 47607350),
('Stephen', 'Curry', 36, 'Davidson', 'PG', 185, 'Active', 2, '6-2', '1988-03-14', 15, 55000000, 51915615);

INSERT INTO TeamsPlayers (player_id, team_id, joined_date, jersey_num) VALUES
(1, 1, '2023-02-09', 7),
(2, 1, '2023-02-06', 11),
(3, 2, '2018-07-01', 23),
(4, 3, '2009-06-25', 30);

INSERT INTO Game (game_date, game_time, home_team_id, away_team_id, home_score, away_score, season, game_type, status, venue) VALUES
('2025-01-15', '19:30:00', 1, 2, 118, 112, '2024-25', 'regular', 'completed', 'Barclays Center'),
('2025-01-18', '20:00:00', 3, 1, 125, 120, '2024-25', 'regular', 'completed', 'Chase Center'),
('2025-01-25', '19:00:00', 1, 4, NULL, NULL, '2024-25', 'regular', 'scheduled', 'Barclays Center');

INSERT INTO PlayerGameStats (player_id, game_id, points, rebounds, assists, steals, blocks, minutes_played) VALUES
(1, 1, 35, 8, 5, 1, 2, 38),
(2, 1, 28, 4, 8, 2, 0, 36),
(3, 1, 32, 10, 7, 1, 1, 37),
(1, 2, 30, 6, 4, 0, 1, 35),
(4, 2, 38, 5, 11, 3, 0, 36);