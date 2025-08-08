CREATE SCHEMA IF NOT EXISTS BallWatch;
USE BallWatch;


DROP TABLE IF EXISTS DataErrors;
DROP TABLE IF EXISTS ErrorLogs;
DROP TABLE IF EXISTS DataLoads;
DROP TABLE IF EXISTS SystemHealth;
DROP TABLE IF EXISTS GamePlan;
DROP TABLE IF EXISTS KeyMatchups;
DROP TABLE IF EXISTS GamePlayers;
DROP TABLE IF EXISTS PlayerGameStats;
DROP TABLE IF EXISTS PlayerMatchup;
DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS TeamsPlayers;
DROP TABLE IF EXISTS DraftEval;
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
       ON UPDATE CASCADE
       ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS Teams (
   team_id INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(100) NOT NULL,
   conference ENUM('Eastern', 'Western') NOT NULL,
   abrv VARCHAR(5) UNIQUE NOT NULL,
   division VARCHAR(50) NOT NULL,
   head_coach VARCHAR(100),
   offensive_system VARCHAR(100),
   defensive_system VARCHAR(100)
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
       REFERENCES Teams(team_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS PlayerLineups (
   player_id INT,
   lineup_id INT,
   position_in_lineup VARCHAR(50),
   PRIMARY KEY (player_id, lineup_id),
   CONSTRAINT FK_PlayerLineups_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_PlayerLineups_LineupConfiguration FOREIGN KEY (lineup_id)
       REFERENCES LineupConfiguration(lineup_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS DraftEval (
   player_id INT,
   team_id INT,
   ranking INT,
   notes TEXT,
   last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   nba_player_comparison VARCHAR(100),
   PRIMARY KEY (player_id, team_id),
   CONSTRAINT FK_DraftEval_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_DraftEval_Teams FOREIGN KEY (team_id)
       REFERENCES Teams(team_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS TeamsPlayers (
   player_id INT,
   team_id INT,
   joined_date DATE,
   jersey_num INT CHECK (jersey_num BETWEEN 0 AND 99),
   left_date DATE,
   PRIMARY KEY (player_id, team_id, joined_date),
   CONSTRAINT FK_TeamsPlayers_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_TeamsPlayers_Teams FOREIGN KEY (team_id)
       REFERENCES Teams(team_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT CHK_Dates CHECK (left_date IS NULL OR left_date >= joined_date)
);


CREATE TABLE IF NOT EXISTS Game (
   game_id INT PRIMARY KEY AUTO_INCREMENT,
   date DATE NOT NULL,
   season VARCHAR(20) NOT NULL,
   is_playoff BOOLEAN DEFAULT FALSE,
   home_team_id INT NOT NULL,
   away_team_id INT NOT NULL,
   home_score INT DEFAULT 0,
   away_score INT DEFAULT 0,
   league_id INT DEFAULT 1,
   CONSTRAINT FK_Game_HomeTeam FOREIGN KEY (home_team_id)
       REFERENCES Teams(team_id)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   CONSTRAINT FK_Game_AwayTeam FOREIGN KEY (away_team_id)
       REFERENCES Teams(team_id)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   CONSTRAINT CHK_DifferentTeams CHECK (home_team_id != away_team_id)
);


CREATE TABLE IF NOT EXISTS PlayerMatchup (
   game_id INT,
   offensive_player_id INT,
   defensive_player_id INT,
   offensive_rating DECIMAL(5,2),
   defensive_rating DECIMAL(5,2),
   possessions INT,
   points_scored INT,
   shooting_percentage DECIMAL(5,2) CHECK (shooting_percentage BETWEEN 0 AND 1),
   PRIMARY KEY (game_id, offensive_player_id, defensive_player_id),
   CONSTRAINT FK_PlayerMatchup_Game FOREIGN KEY (game_id)
       REFERENCES Game(game_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_PlayerMatchup_OffensivePlayer FOREIGN KEY (offensive_player_id)
       REFERENCES Players(player_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_PlayerMatchup_DefensivePlayer FOREIGN KEY (defensive_player_id)
       REFERENCES Players(player_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS PlayerGameStats (
   player_id INT,
   game_id INT,
   team_id INT,
   points INT DEFAULT 0,
   rebounds INT DEFAULT 0,
   assists INT DEFAULT 0,
   shooting_percentage DECIMAL(5,2) CHECK (shooting_percentage BETWEEN 0 AND 1),
   plus_minus INT DEFAULT 0,
   minutes_played INT CHECK (minutes_played BETWEEN 0 AND 48),
   turnovers INT DEFAULT 0,
   steals INT DEFAULT 0,
   blocks INT DEFAULT 0,
   fouls_committed INT DEFAULT 0,
   PRIMARY KEY (player_id, game_id),
   CONSTRAINT FK_PlayerGameStats_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_PlayerGameStats_Game FOREIGN KEY (game_id)
       REFERENCES Game(game_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_PlayerGameStats_Teams FOREIGN KEY (team_id)
       REFERENCES Teams(team_id)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS KeyMatchups (
   matchup_id INT PRIMARY KEY AUTO_INCREMENT,
   matchup_text TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS GamePlan (
   gp_id INT PRIMARY KEY AUTO_INCREMENT,
   game_id INT UNIQUE,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   updated_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   offensive_strategy TEXT,
   special_situations TEXT,
   defensive_strategy TEXT,
   key_matchups INT,
   CONSTRAINT FK_GamePlan_Game FOREIGN KEY (game_id)
       REFERENCES Game(game_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_GamePlan_KeyMatchups FOREIGN KEY (key_matchups)
       REFERENCES KeyMatchups(matchup_id)
       ON UPDATE CASCADE
       ON DELETE SET NULL
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
   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
   error_type VARCHAR(100),
   error_message TEXT,
   service_component VARCHAR(100),
   user_id INT,
   CONSTRAINT FK_ErrorLogs_Users FOREIGN KEY (user_id)
       REFERENCES Users(user_id)
       ON UPDATE CASCADE
       ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS DataLoads (
   load_id INT PRIMARY KEY AUTO_INCREMENT,
   load_date DATE NOT NULL,
   data_source VARCHAR(100),
   status ENUM('Started', 'Completed', 'Failed', 'In Progress') DEFAULT 'Started',
   start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
   end_time DATETIME,
   load_time TIME
);


CREATE TABLE IF NOT EXISTS DataErrors (
   load_id INT,
   error_id INT,
   PRIMARY KEY (load_id, error_id),
   CONSTRAINT FK_DataErrors_DataLoads FOREIGN KEY (load_id)
       REFERENCES DataLoads(load_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   CONSTRAINT FK_DataErrors_ErrorLogs FOREIGN KEY (error_id)
       REFERENCES ErrorLogs(error_id)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);
