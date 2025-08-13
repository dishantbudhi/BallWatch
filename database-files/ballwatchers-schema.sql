CREATE SCHEMA IF NOT EXISTS BallWatch;
USE BallWatch;

DROP TABLE IF EXISTS PlayerMatchup;
DROP TABLE IF EXISTS PlayerGameStats;
DROP TABLE IF EXISTS PlayerLineups;
DROP TABLE IF EXISTS TeamsPlayers;
DROP TABLE IF EXISTS DraftEvaluations;
DROP TABLE IF EXISTS GamePlans;
DROP TABLE IF EXISTS SystemLogs;
DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS LineupConfiguration;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS Teams;
DROP TABLE IF EXISTS Agent;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
   user_id INT PRIMARY KEY AUTO_INCREMENT,
   email VARCHAR(100) UNIQUE NOT NULL,
   username VARCHAR(50) UNIQUE NOT NULL,
   role VARCHAR(20) NOT NULL,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE Agent (
   agent_id INT PRIMARY KEY AUTO_INCREMENT,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   agency_name VARCHAR(100),
   phone VARCHAR(20),
   email VARCHAR(100) UNIQUE
);

CREATE TABLE Teams (
   team_id INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(100) NOT NULL,
   city VARCHAR(50),
   conference VARCHAR(10) NOT NULL,
   division VARCHAR(50) NOT NULL,
   coach VARCHAR(100),
   arena VARCHAR(100),
   founded_year INT,
   championships INT DEFAULT 0,
   offensive_system VARCHAR(100),
   defensive_system VARCHAR(100)
);

CREATE TABLE Players (
   player_id INT PRIMARY KEY AUTO_INCREMENT,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   age INT,
   height VARCHAR(10),
   weight INT,
   college VARCHAR(100),
   position VARCHAR(20),
   years_exp INT DEFAULT 0,
   draft_year INT,
   player_status VARCHAR(20) DEFAULT 'Active',
   dominant_hand VARCHAR(10) DEFAULT 'Right',
   expected_salary DECIMAL(12,2),
   current_salary DECIMAL(12,2),
   agent_id INT,
   picture TEXT,
   DOB DATE,
   CONSTRAINT FK_Players_Agent FOREIGN KEY (agent_id) REFERENCES Agent(agent_id)
       ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE TeamsPlayers (
   player_id INT,
   team_id INT,
   joined_date DATE,
   jersey_num INT,
   left_date DATE,
   status VARCHAR(20) DEFAULT 'active',
   PRIMARY KEY (player_id, team_id, joined_date),
   CONSTRAINT FK_TeamsPlayers_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_TeamsPlayers_Teams FOREIGN KEY (team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Game (
   game_id INT PRIMARY KEY AUTO_INCREMENT,
   game_date DATE NOT NULL,
   game_time TIME,
   home_team_id INT NOT NULL,
   away_team_id INT NOT NULL,
   home_score INT DEFAULT 0,
   away_score INT DEFAULT 0,
   season VARCHAR(20) NOT NULL,
   game_type VARCHAR(20) DEFAULT 'regular',
   status VARCHAR(20) DEFAULT 'scheduled',
   attendance INT,
   venue VARCHAR(100),
   CONSTRAINT FK_Game_HomeTeam FOREIGN KEY (home_team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT FK_Game_AwayTeam FOREIGN KEY (away_team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE PlayerGameStats (
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

CREATE TABLE PlayerMatchup (
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

CREATE TABLE LineupConfiguration (
   lineup_id INT PRIMARY KEY AUTO_INCREMENT,
   team_id INT NOT NULL,
   quarter INT,
   time_on TIME,
   time_off TIME,
   plus_minus INT,
   offensive_rating DECIMAL(5,2),
   defensive_rating DECIMAL(5,2),
   CONSTRAINT FK_LineupConfiguration_Teams FOREIGN KEY (team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE PlayerLineups (
   player_id INT,
   lineup_id INT,
   position_in_lineup VARCHAR(50),
   PRIMARY KEY (player_id, lineup_id),
   CONSTRAINT FK_PlayerLineups_Players FOREIGN KEY (player_id)
       REFERENCES Players(player_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_PlayerLineups_LineupConfiguration FOREIGN KEY (lineup_id)
       REFERENCES LineupConfiguration(lineup_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE DraftEvaluations (
   evaluation_id INT PRIMARY KEY AUTO_INCREMENT,
   player_id INT NOT NULL,
   overall_rating DECIMAL(5,2),
   offensive_rating DECIMAL(5,2),
   defensive_rating DECIMAL(5,2),
   athleticism_rating DECIMAL(5,2),
   potential_rating DECIMAL(5,2),
   evaluation_type VARCHAR(20) DEFAULT 'prospect',
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

CREATE TABLE GamePlans (
   plan_id INT PRIMARY KEY AUTO_INCREMENT,
   team_id INT NOT NULL,
   opponent_id INT,
   game_id INT,
   plan_name VARCHAR(200) NOT NULL,
   offensive_strategy TEXT,
   defensive_strategy TEXT,
   key_matchups TEXT,
   special_instructions TEXT,
   status VARCHAR(20) DEFAULT 'draft',
   created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
   updated_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   CONSTRAINT FK_GamePlans_Team FOREIGN KEY (team_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_GamePlans_Opponent FOREIGN KEY (opponent_id)
       REFERENCES Teams(team_id) ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT FK_GamePlans_Game FOREIGN KEY (game_id)
       REFERENCES Game(game_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE SystemLogs (
   log_id INT PRIMARY KEY AUTO_INCREMENT,
   log_type VARCHAR(50) NOT NULL,
   service_name VARCHAR(100),
   severity VARCHAR(20) NOT NULL,
   message TEXT,
   error_rate_pct DECIMAL(5,2),
   response_time DECIMAL(10,2),
   records_processed INT,
   records_failed INT,
   source_file VARCHAR(255),
   user_id INT,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
   resolved_at DATETIME,
   resolved_by VARCHAR(100),
   resolution_notes TEXT,
   CONSTRAINT FK_SystemLogs_Users FOREIGN KEY (user_id)
       REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE SET NULL
);