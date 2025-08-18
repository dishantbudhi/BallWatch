-- Performance indexes for BallWatch schema
USE BallWatch;

-- PlayerGameStats: queries often filter by game_id or player_id separately
CREATE INDEX idx_pgs_player_id ON PlayerGameStats (player_id);
CREATE INDEX idx_pgs_game_id ON PlayerGameStats (game_id);

-- TeamsPlayers: filter by team_id with left_date NULL and by player_id current team
CREATE INDEX idx_tp_team_current ON TeamsPlayers (team_id, left_date);
CREATE INDEX idx_tp_player_current ON TeamsPlayers (player_id, left_date);

-- Game: common filters
CREATE INDEX idx_game_date ON Game (game_date);
CREATE INDEX idx_game_season ON Game (season);
CREATE INDEX idx_game_status ON Game (status);
CREATE INDEX idx_game_teams ON Game (home_team_id, away_team_id);

-- DraftEvaluations: sort/filter by overall_rating and evaluation_type
CREATE INDEX idx_de_overall_type ON DraftEvaluations (overall_rating, evaluation_type);

-- SystemLogs: cleanup and reporting filters
CREATE INDEX idx_logs_created ON SystemLogs (created_at);
CREATE INDEX idx_logs_service ON SystemLogs (service_name);
CREATE INDEX idx_logs_severity ON SystemLogs (severity);
CREATE INDEX idx_logs_resolved ON SystemLogs (resolved_at);


