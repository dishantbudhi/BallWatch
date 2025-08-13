USE BallWatch;

-- Clear existing data to prevent duplicates
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM ValidationReports;
DELETE FROM CleanupHistory;
DELETE FROM CleanupSchedule;
DELETE FROM DataErrors;
DELETE FROM ErrorLogs;
DELETE FROM DataLoads;
DELETE FROM SystemHealth;
DELETE FROM GamePlans;
DELETE FROM KeyMatchups;
DELETE FROM GamePlayers;
DELETE FROM PlayerGameStats;
DELETE FROM PlayerMatchup;
DELETE FROM Game;
DELETE FROM TeamsPlayers;
DELETE FROM DraftEvaluations;
DELETE FROM PlayerLineups;
DELETE FROM LineupConfiguration;
DELETE FROM Teams;
DELETE FROM Players;
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
ALTER TABLE LineupConfiguration AUTO_INCREMENT = 1;
ALTER TABLE KeyMatchups AUTO_INCREMENT = 1;
ALTER TABLE SystemHealth AUTO_INCREMENT = 1;
ALTER TABLE ErrorLogs AUTO_INCREMENT = 1;
ALTER TABLE DataLoads AUTO_INCREMENT = 1;
ALTER TABLE DataErrors AUTO_INCREMENT = 1;
ALTER TABLE CleanupSchedule AUTO_INCREMENT = 1;
ALTER TABLE CleanupHistory AUTO_INCREMENT = 1;
ALTER TABLE ValidationReports AUTO_INCREMENT = 1;

-- Users (35 rows - mix of roles)
INSERT INTO Users (email, username, role) VALUES
('mike.lewis@ballwatch.com', 'mlewis', 'admin'),
('sarah.johnson@ballwatch.com', 'sjohnson', 'admin'),
('marcus.thompson@nets.com', 'mthompson', 'coach'),
('andre.wu@nets.com', 'awu', 'gm'),
('steve.kerr@warriors.com', 'skerr', 'coach'),
('bob.myers@warriors.com', 'bmyers', 'gm'),
('joe.mazzulla@celtics.com', 'jmazzulla', 'coach'),
('brad.stevens@celtics.com', 'bstevens', 'gm'),
('darvin.ham@lakers.com', 'dham', 'coach'),
('rob.pelinka@lakers.com', 'rpelinka', 'gm'),
('erik.spoelstra@heat.com', 'espoelstra', 'coach'),
('pat.riley@heat.com', 'priley', 'gm'),
('doc.rivers@sixers.com', 'drivers', 'coach'),
('daryl.morey@sixers.com', 'dmorey', 'gm'),
('tom.thibodeau@knicks.com', 'tthib', 'coach'),
('leon.rose@knicks.com', 'lrose', 'gm'),
('mike.budenholzer@suns.com', 'mbud', 'coach'),
('james.jones@suns.com', 'jjones', 'gm'),
('jason.kidd@mavs.com', 'jkidd', 'coach'),
('nico.harrison@mavs.com', 'nharrison', 'gm'),
('billy.donovan@bulls.com', 'bdonovan', 'coach'),
('arturas.karnisovas@bulls.com', 'akarnisovas', 'gm'),
('data.analyst@ballwatch.com', 'analyst1', 'analyst'),
('scout.martinez@ballwatch.com', 'smartinez', 'analyst'),
('stats.guru@ballwatch.com', 'statsguru', 'analyst'),
('performance.coach@ballwatch.com', 'pcoach', 'analyst'),
('video.coordinator@ballwatch.com', 'vcoord', 'analyst'),
('advance.scout@ballwatch.com', 'ascout', 'analyst'),
('johnny.evans@gmail.com', 'jevans25', 'fan'),
('basketball.fan@gmail.com', 'hoopsfan', 'fan'),
('nba.superfan@yahoo.com', 'superfan1', 'fan'),
('courtside.viewer@hotmail.com', 'courtside', 'fan'),
('stats.nerd@gmail.com', 'statsnerd', 'fan'),
('longtime.fan@aol.com', 'longtime', 'fan'),
('casual.viewer@gmail.com', 'casual', 'fan');

-- Agents (32 rows - realistic agent data)
INSERT INTO Agent (first_name, last_name, agency_name, phone, email) VALUES
('Rich', 'Paul', 'Klutch Sports Group', '555-0101', 'rich@klutchsports.com'),
('Jeff', 'Schwartz', 'Excel Sports Management', '555-0102', 'jeff@excelsports.com'),
('Mark', 'Bartelstein', 'Priority Sports', '555-0103', 'mark@prioritysports.com'),
('Bill', 'Duffy', 'BDA Sports Management', '555-0104', 'bill@bdasports.com'),
('Austin', 'Brown', 'CAA Sports', '555-0105', 'austin@caasports.com'),
('Aaron', 'Mintz', 'CAA Sports', '555-0106', 'aaron@caasports.com'),
('Leon', 'Rose', 'CAA Sports', '555-0107', 'leon@caasports.com'),
('Rob', 'Pelinka', 'The Landmark Sports Agency', '555-0108', 'rob@landmark.com'),
('Dan', 'Fegan', 'Independent', '555-0109', 'dan@feganagency.com'),
('Andy', 'Miller', 'ASM Sports', '555-0110', 'andy@asmsports.com'),
('Bernie', 'Lee', 'Roc Nation Sports', '555-0111', 'bernie@rocnation.com'),
('Happy', 'Walters', 'Wasserman Media Group', '555-0112', 'happy@wasserman.com'),
('David', 'Falk', 'FAME', '555-0113', 'david@fame.com'),
('Arn', 'Tellem', 'Wasserman Media Group', '555-0114', 'arn@wasserman.com'),
('Raymond', 'Brothers', 'Roc Nation Sports', '555-0115', 'raymond@rocnation.com'),
('Michael', 'Tellem', 'Wasserman Media Group', '555-0116', 'michael@wasserman.com'),
('Jason', 'Glushon', 'Glushon Sports Management', '555-0117', 'jason@glushon.com'),
('Sam', 'Goldfeder', 'Excel Sports Management', '555-0118', 'sam@excelsports.com'),
('Thad', 'Foucher', 'Wasserman Media Group', '555-0119', 'thad@wasserman.com'),
('B.J.', 'Armstrong', 'Wasserman Media Group', '555-0120', 'bj@wasserman.com'),
('Mark', 'Termini', 'Octagon', '555-0121', 'mark@octagon.com'),
('Christian', 'Dawkins', 'ASM Sports', '555-0122', 'christian@asmsports.com'),
('Cervando', 'Maldonado', 'Maldonado Sports', '555-0123', 'cervando@maldonado.com'),
('George', 'Langberg', 'Wasserman Media Group', '555-0124', 'george@wasserman.com'),
('Joel', 'Bell', 'Wasserman Media Group', '555-0125', 'joel@wasserman.com'),
('Jordan', 'Gertler', 'Excel Sports Management', '555-0126', 'jordan@excelsports.com'),
('Mike', 'George', 'One Legacy Sports', '555-0127', 'mike@onelegacy.com'),
('Nima', 'Namakian', 'Octagon', '555-0128', 'nima@octagon.com'),
('Omar', 'Wilkes', 'Wasserman Media Group', '555-0129', 'omar@wasserman.com'),
('Paul', 'Graham', 'Independent', '555-0130', 'paul@graham.com'),
('Steven', 'Heumann', 'CAA Sports', '555-0131', 'steven@caasports.com'),
('Wallace', 'Prather', 'Octagon', '555-0132', 'wallace@octagon.com');

-- Teams (30 teams - full NBA)
INSERT INTO Teams (name, conference, division, coach, gm, offensive_system, defensive_system, city, state, arena, founded_year, championships) VALUES
('Brooklyn Nets', 'Eastern', 'Atlantic', 'Marcus Thompson', 'Andre Wu', 'Motion Offense', 'Switch Everything', 'Brooklyn', 'NY', 'Barclays Center', 1967, 0),
('Boston Celtics', 'Eastern', 'Atlantic', 'Joe Mazzulla', 'Brad Stevens', 'Five Out', 'Switch Defense', 'Boston', 'MA', 'TD Garden', 1946, 17),
('New York Knicks', 'Eastern', 'Atlantic', 'Tom Thibodeau', 'Leon Rose', 'Pick and Roll Heavy', 'Aggressive Defense', 'New York', 'NY', 'Madison Square Garden', 1946, 2),
('Philadelphia 76ers', 'Eastern', 'Atlantic', 'Doc Rivers', 'Daryl Morey', 'Inside-Out', 'Switch Defense', 'Philadelphia', 'PA', 'Wells Fargo Center', 1949, 3),
('Toronto Raptors', 'Eastern', 'Atlantic', 'Darko Rajakovic', 'Bobby Webster', 'Motion Offense', 'Zone Defense', 'Toronto', 'ON', 'Scotiabank Arena', 1995, 1),
('Chicago Bulls', 'Eastern', 'Central', 'Billy Donovan', 'Arturas Karnisovas', 'Ball Movement', 'Switch Defense', 'Chicago', 'IL', 'United Center', 1966, 6),
('Cleveland Cavaliers', 'Eastern', 'Central', 'J.B. Bickerstaff', 'Koby Altman', 'Inside-Out', 'Drop Coverage', 'Cleveland', 'OH', 'Rocket Mortgage FieldHouse', 1970, 1),
('Detroit Pistons', 'Eastern', 'Central', 'Monty Williams', 'Troy Weaver', 'Motion Offense', 'Switch Defense', 'Detroit', 'MI', 'Little Caesars Arena', 1941, 3),
('Indiana Pacers', 'Eastern', 'Central', 'Rick Carlisle', 'Chad Buchanan', 'Pace and Space', 'Switch Defense', 'Indianapolis', 'IN', 'Gainbridge Fieldhouse', 1967, 0),
('Milwaukee Bucks', 'Eastern', 'Central', 'Adrian Griffin', 'Jon Horst', 'Five Out', 'Drop Coverage', 'Milwaukee', 'WI', 'Fiserv Forum', 1968, 1),
('Atlanta Hawks', 'Eastern', 'Southeast', 'Quin Snyder', 'Landry Fields', 'Pick and Roll Heavy', 'Switch Defense', 'Atlanta', 'GA', 'State Farm Arena', 1946, 1),
('Charlotte Hornets', 'Eastern', 'Southeast', 'Steve Clifford', 'Mitch Kupchak', 'Motion Offense', 'Switch Defense', 'Charlotte', 'NC', 'Spectrum Center', 1988, 0),
('Miami Heat', 'Eastern', 'Southeast', 'Erik Spoelstra', 'Pat Riley', 'Zone Attack', 'Zone Defense', 'Miami', 'FL', 'FTX Arena', 1988, 3),
('Orlando Magic', 'Eastern', 'Southeast', 'Jamahl Mosley', 'Jeff Weltman', 'Motion Offense', 'Switch Defense', 'Orlando', 'FL', 'Amway Center', 1989, 0),
('Washington Wizards', 'Eastern', 'Southeast', 'Wes Unseld Jr.', 'Tommy Sheppard', 'Pick and Roll Heavy', 'Switch Defense', 'Washington', 'DC', 'Capital One Arena', 1961, 1),
('Denver Nuggets', 'Western', 'Northwest', 'Michael Malone', 'Calvin Booth', 'Inside-Out', 'Switch Defense', 'Denver', 'CO', 'Ball Arena', 1976, 1),
('Minnesota Timberwolves', 'Western', 'Northwest', 'Chris Finch', 'Tim Connelly', 'Motion Offense', 'Switch Defense', 'Minneapolis', 'MN', 'Target Center', 1989, 0),
('Oklahoma City Thunder', 'Western', 'Northwest', 'Mark Daigneault', 'Sam Presti', 'Motion Offense', 'Switch Defense', 'Oklahoma City', 'OK', 'Paycom Center', 1967, 1),
('Portland Trail Blazers', 'Western', 'Northwest', 'Chauncey Billups', 'Joe Cronin', 'Pick and Roll Heavy', 'Switch Defense', 'Portland', 'OR', 'Moda Center', 1970, 1),
('Utah Jazz', 'Western', 'Northwest', 'Will Hardy', 'Justin Zanik', 'Motion Offense', 'Drop Coverage', 'Salt Lake City', 'UT', 'Vivint Arena', 1974, 0),
('Golden State Warriors', 'Western', 'Pacific', 'Steve Kerr', 'Bob Myers', 'Motion Offense', 'Aggressive Switching', 'San Francisco', 'CA', 'Chase Center', 1946, 7),
('Los Angeles Clippers', 'Western', 'Pacific', 'Tyronn Lue', 'Lawrence Frank', 'Pick and Roll Heavy', 'Switch Defense', 'Los Angeles', 'CA', 'Crypto.com Arena', 1970, 0),
('Los Angeles Lakers', 'Western', 'Pacific', 'Darvin Ham', 'Rob Pelinka', 'LeBron System', 'Drop Coverage', 'Los Angeles', 'CA', 'Crypto.com Arena', 1947, 17),
('Phoenix Suns', 'Western', 'Pacific', 'Mike Budenholzer', 'James Jones', 'Pick and Roll Heavy', 'Switch Defense', 'Phoenix', 'AZ', 'Footprint Center', 1968, 0),
('Sacramento Kings', 'Western', 'Pacific', 'Mike Brown', 'Monte McNair', 'Pace and Space', 'Switch Defense', 'Sacramento', 'CA', 'Golden 1 Center', 1945, 1),
('Dallas Mavericks', 'Western', 'Southwest', 'Jason Kidd', 'Nico Harrison', 'Pick and Roll Heavy', 'Switch Defense', 'Dallas', 'TX', 'American Airlines Center', 1980, 1),
('Houston Rockets', 'Western', 'Southwest', 'Ime Udoka', 'Rafael Stone', 'Motion Offense', 'Switch Defense', 'Houston', 'TX', 'Toyota Center', 1971, 2),
('Memphis Grizzlies', 'Western', 'Southwest', 'Taylor Jenkins', 'Zach Kleiman', 'Motion Offense', 'Aggressive Defense', 'Memphis', 'TN', 'FedExForum', 1995, 0),
('New Orleans Pelicans', 'Western', 'Southwest', 'Willie Green', 'David Griffin', 'Inside-Out', 'Switch Defense', 'New Orleans', 'LA', 'Smoothie King Center', 1988, 0),
('San Antonio Spurs', 'Western', 'Southwest', 'Gregg Popovich', 'Brian Wright', 'Ball Movement', 'Team Defense', 'San Antonio', 'TX', 'Frost Bank Center', 1967, 5);

-- Players (38 rows - diverse mix of NBA talent)
INSERT INTO Players (first_name, last_name, age, college, position, weight, player_status, agent_id,
                   height, DOB, years_exp, dominant_hand, expected_salary, player_type, current_salary, draft_year) VALUES
-- Superstars
('Kevin', 'Durant', 35, 'Texas', 'SF', 240, 'Active', 1, '6-10', '1988-09-29', 16, 'Right', 51000000, 'Superstar', 47649433, 2007),
('LeBron', 'James', 39, NULL, 'SF', 250, 'Active', 1, '6-9', '1984-12-30', 21, 'Right', 51000000, 'Superstar', 47607350, 2003),
('Stephen', 'Curry', 36, 'Davidson', 'PG', 185, 'Active', 2, '6-2', '1988-03-14', 15, 'Right', 55000000, 'Superstar', 51915615, 2009),
('Nikola', 'Jokic', 29, NULL, 'C', 284, 'Active', 3, '6-11', '1995-02-19', 9, 'Right', 50000000, 'Superstar', 47607350, 2014),
('Giannis', 'Antetokounmpo', 29, NULL, 'PF', 243, 'Active', 4, '6-11', '1994-12-06', 11, 'Right', 55000000, 'Superstar', 45640084, 2013),
('Joel', 'Embiid', 30, 'Kansas', 'C', 280, 'Active', 5, '7-0', '1994-03-16', 10, 'Right', 52000000, 'Superstar', 47607350, 2014),
('Luka', 'Doncic', 25, NULL, 'PG', 230, 'Active', 6, '6-7', '1999-02-28', 6, 'Right', 48000000, 'Superstar', 40064220, 2018),
('Jayson', 'Tatum', 26, 'Duke', 'SF', 210, 'Active', 2, '6-8', '1998-03-03', 7, 'Right', 35000000, 'All-Star', 32600060, 2017),

-- All-Stars
('Kyrie', 'Irving', 32, 'Duke', 'PG', 195, 'Active', 2, '6-2', '1992-03-23', 13, 'Right', 42000000, 'All-Star', 37037037, 2011),
('Jimmy', 'Butler', 34, 'Marquette', 'SF', 230, 'Active', 1, '6-7', '1989-09-14', 13, 'Right', 48000000, 'All-Star', 48798677, 2011),
('Kawhi', 'Leonard', 33, 'San Diego State', 'SF', 225, 'Active', 7, '6-7', '1991-06-29', 13, 'Right', 45000000, 'All-Star', 45640084, 2011),
('Paul', 'George', 34, 'Fresno State', 'SF', 220, 'Active', 8, '6-8', '1990-05-02', 14, 'Right', 42000000, 'All-Star', 45640084, 2010),
('Damian', 'Lillard', 33, 'Weber State', 'PG', 195, 'Active', 9, '6-2', '1990-07-15', 12, 'Right', 48000000, 'All-Star', 48787676, 2012),
('Anthony', 'Davis', 31, 'Kentucky', 'PF', 253, 'Active', 1, '6-10', '1993-03-11', 12, 'Right', 45000000, 'All-Star', 40600080, 2012),
('Ben', 'Simmons', 28, 'LSU', 'PF', 240, 'Active', 1, '6-10', '1996-07-20', 8, 'Left', 40000000, 'All-Star', 37893408, 2016),
('Trae', 'Young', 25, 'Oklahoma', 'PG', 164, 'Active', 10, '6-1', '1998-09-19', 6, 'Right', 38000000, 'All-Star', 37096500, 2018),
('Donovan', 'Mitchell', 27, 'Louisville', 'SG', 215, 'Active', 11, '6-1', '1996-09-07', 7, 'Right', 35000000, 'All-Star', 33162030, 2017),
('Devin', 'Booker', 27, 'Kentucky', 'SG', 206, 'Active', 12, '6-5', '1996-10-30', 9, 'Right', 40000000, 'All-Star', 36016200, 2015),

-- Solid Starters
('Tyler', 'Herro', 24, 'Kentucky', 'SG', 195, 'Active', 13, '6-5', '2000-01-20', 5, 'Right', 25000000, 'Starter', 27000000, 2019),
('Mikal', 'Bridges', 27, 'Villanova', 'SF', 209, 'Active', 14, '6-6', '1996-08-30', 6, 'Right', 22000000, 'Starter', 21700000, 2018),
('OG', 'Anunoby', 26, 'Indiana', 'SF', 232, 'Active', 15, '6-7', '1997-07-17', 7, 'Right', 28000000, 'Starter', 18642857, 2017),
('Jalen', 'Green', 22, NULL, 'SG', 186, 'Active', 16, '6-4', '2002-02-09', 3, 'Right', 15000000, 'Starter', 9873440, 2021),
('Alperen', 'Sengun', 22, NULL, 'C', 243, 'Active', 17, '6-10', '2002-07-25', 3, 'Right', 18000000, 'Starter', 5607120, 2021),
('Scottie', 'Barnes', 23, 'Florida State', 'PF', 227, 'Active', 18, '6-9', '2001-08-01', 3, 'Right', 20000000, 'Starter', 8008440, 2021),
('Franz', 'Wagner', 23, 'Michigan', 'SF', 220, 'Active', 19, '6-10', '2001-08-27', 3, 'Right', 16000000, 'Starter', 5358320, 2021),
('Evan', 'Mobley', 23, 'USC', 'PF', 215, 'Active', 20, '6-11', '2001-06-18', 3, 'Right', 22000000, 'Starter', 8882640, 2021),

-- Role Players
('Marcus', 'Smart', 30, 'Oklahoma State', 'PG', 220, 'Active', 21, '6-3', '1994-03-06', 10, 'Right', 14000000, 'Role Player', 14339285, 2014),
('Robert', 'Williams', 27, 'Texas A&M', 'C', 237, 'Active', 22, '6-9', '1997-10-17', 6, 'Right', 12000000, 'Role Player', 12400000, 2018),
('Derrick', 'White', 29, 'Colorado', 'SG', 190, 'Active', 23, '6-4', '1994-07-02', 7, 'Right', 16000000, 'Role Player', 16500000, 2017),
('Kyle', 'Lowry', 38, 'Villanova', 'PG', 196, 'Active', 24, '6-0', '1986-03-25', 18, 'Right', 8000000, 'Veteran', 29682540, 2006),
('P.J.', 'Tucker', 39, 'Texas', 'PF', 245, 'Active', 25, '6-5', '1985-05-05', 12, 'Right', 6000000, 'Veteran', 11539326, 2006),

-- Promising Young Players
('Cooper', 'Flagg', 18, 'Duke', 'SF', 200, 'Active', 3, '6-9', '2006-12-21', 0, 'Right', 10000000, 'Rookie', 0, 2025),
('Dylan', 'Harper', 19, 'Rutgers', 'SG', 195, 'Active', 26, '6-6', '2005-07-15', 0, 'Right', 8000000, 'Rookie', 0, 2025),
('Ace', 'Bailey', 19, 'Rutgers', 'SF', 200, 'Active', 27, '6-10', '2005-09-12', 0, 'Right', 9000000, 'Rookie', 0, 2025),
('VJ', 'Edgecombe', 19, 'Baylor', 'SG', 180, 'Active', 28, '6-5', '2005-11-03', 0, 'Right', 7000000, 'Rookie', 0, 2025),
('Nolan', 'Traore', 19, NULL, 'C', 245, 'Active', 29, '6-11', '2005-05-22', 0, 'Right', 6000000, 'Rookie', 0, 2025),

-- International Prospects
('Hugo', 'Gonzalez', 20, NULL, 'PG', 185, 'Active', 30, '6-3', '2004-08-14', 1, 'Right', 5000000, 'Prospect', 2500000, 2024),
('Luka', 'Radovic', 21, NULL, 'SF', 210, 'Active', 31, '6-8', '2003-12-07', 1, 'Right', 4000000, 'Prospect', 2800000, 2024),
('Nikola', 'Topic', 19, NULL, 'PG', 190, 'Active', 32, '6-6', '2005-03-18', 0, 'Right', 6500000, 'Rookie', 0, 2025);

-- TeamsPlayers Bridge Table (135 rows - includes current and historical assignments)
INSERT INTO TeamsPlayers (player_id, team_id, joined_date, jersey_num, left_date, status) VALUES
-- Current Team Assignments (Active players)
(1, 1, '2023-02-09', 7, NULL, 'active'),  -- KD to Nets
(2, 23, '2018-07-01', 23, NULL, 'active'), -- LeBron to Lakers  
(3, 21, '2009-06-25', 30, NULL, 'active'), -- Curry to Warriors
(4, 17, '2019-02-07', 15, NULL, 'active'), -- Jokic to Nuggets
(5, 10, '2013-06-27', 34, NULL, 'active'), -- Giannis to Bucks
(6, 4, '2014-06-26', 21, NULL, 'active'),  -- Embiid to Sixers
(7, 26, '2018-06-21', 77, NULL, 'active'), -- Luka to Mavs
(8, 2, '2017-06-22', 0, NULL, 'active'),   -- Tatum to Celtics
(9, 1, '2023-02-06', 11, NULL, 'active'),  -- Kyrie to Nets
(10, 13, '2019-07-06', 22, NULL, 'active'), -- Butler to Heat
(11, 22, '2019-07-10', 2, NULL, 'active'), -- Kawhi to Clippers
(12, 22, '2019-07-06', 13, NULL, 'active'), -- PG to Clippers  
(13, 10, '2023-09-27', 0, NULL, 'active'), -- Dame to Bucks
(14, 23, '2019-06-15', 3, NULL, 'active'), -- AD to Lakers
(15, 1, '2022-02-10', 10, NULL, 'active'), -- Ben Simmons to Nets
(16, 11, '2018-06-21', 11, NULL, 'active'), -- Trae to Hawks
(17, 7, '2022-09-01', 45, NULL, 'active'), -- Mitchell to Cavs
(18, 24, '2015-06-25', 1, NULL, 'active'), -- Booker to Suns
(19, 13, '2019-06-20', 14, NULL, 'active'), -- Herro to Heat
(20, 3, '2023-12-30', 1, NULL, 'active'),  -- Mikal to Knicks
(21, 3, '2023-12-30', 8, NULL, 'active'),  -- OG to Knicks
(22, 27, '2021-07-29', 0, NULL, 'active'), -- Jalen Green to Rockets
(23, 27, '2021-07-29', 28, NULL, 'active'), -- Sengun to Rockets
(24, 5, '2021-07-29', 4, NULL, 'active'),  -- Barnes to Raptors
(25, 14, '2021-07-29', 22, NULL, 'active'), -- Franz to Magic
(26, 7, '2021-07-29', 4, NULL, 'active'),  -- Mobley to Cavs
(27, 13, '2022-02-10', 36, NULL, 'active'), -- Smart to Heat
(28, 2, '2021-02-25', 44, NULL, 'active'), -- Rob Williams to Celtics
(29, 2, '2022-02-10', 9, NULL, 'active'),  -- Derrick White to Celtics
(30, 13, '2022-08-06', 7, NULL, 'active'), -- Lowry to Heat
(31, 22, '2022-07-01', 17, NULL, 'active'), -- PJ Tucker to Clippers
(32, 21, '2025-06-26', 1, NULL, 'active'), -- Flagg to Warriors (fictional draft)
(33, 3, '2025-06-26', 2, NULL, 'active'),  -- Harper to Knicks
(34, 4, '2025-06-26', 3, NULL, 'active'),  -- Bailey to Sixers
(35, 13, '2025-06-26', 4, NULL, 'active'), -- Edgecombe to Heat
(36, 29, '2025-06-26', 5, NULL, 'active'), -- Traore to Pelicans
(37, 28, '2024-06-26', 6, NULL, 'active'), -- Hugo to Grizzlies
(38, 20, '2024-06-26', 7, NULL, 'active'), -- Radovic to Jazz

-- Historical Team Assignments (Players who switched teams)
(1, 21, '2016-07-07', 35, '2019-06-30', 'inactive'), -- KD Warriors
(1, 24, '2019-07-07', 7, '2023-02-08', 'inactive'),  -- KD Suns
(2, 7, '2014-07-11', 23, '2018-06-30', 'inactive'),  -- LeBron Cavs (return)
(2, 13, '2010-07-08', 6, '2014-07-11', 'inactive'),  -- LeBron Heat
(2, 7, '2003-06-26', 23, '2010-07-08', 'inactive'),  -- LeBron Cavs (original)
(9, 2, '2017-08-22', 11, '2019-06-30', 'inactive'),  -- Kyrie Celtics  
(9, 1, '2019-07-01', 11, '2023-02-05', 'inactive'),  -- Kyrie Nets (first stint)
(9, 7, '2011-06-23', 2, '2017-08-22', 'inactive'),   -- Kyrie Cavs
(10, 6, '2011-06-23', 21, '2017-07-06', 'inactive'), -- Butler Bulls
(10, 17, '2017-07-06', 23, '2018-11-12', 'inactive'), -- Butler Timberwolves
(10, 4, '2018-11-12', 23, '2019-07-06', 'inactive'), -- Butler Sixers
(11, 20, '2011-06-23', 2, '2018-07-18', 'inactive'), -- Kawhi Spurs
(11, 5, '2018-07-18', 2, '2019-07-10', 'inactive'),  -- Kawhi Raptors
(12, 9, '2010-06-24', 24, '2017-07-06', 'inactive'), -- PG Pacers
(12, 16, '2017-07-06', 13, '2019-07-06', 'inactive'), -- PG Thunder
(13, 19, '2012-06-28', 0, '2021-07-30', 'inactive'), -- Dame Blazers
(14, 29, '2012-06-28', 23, '2019-06-15', 'inactive'), -- AD Pelicans
(15, 4, '2016-06-23', 25, '2022-02-10', 'inactive'), -- Simmons Sixers
(17, 20, '2017-06-23', 45, '2022-09-01', 'inactive'), -- Mitchell Jazz
(27, 2, '2014-06-26', 36, '2022-02-10', 'inactive'), -- Smart Celtics
(28, 2, '2018-06-21', 44, '2021-02-25', 'inactive'), -- Rob Williams draft
(29, 30, '2017-06-23', 4, '2022-02-10', 'inactive'), -- White Spurs
(30, 5, '2006-06-28', 7, '2012-07-11', 'inactive'),  -- Lowry Raptors
(31, 13, '2017-07-07', 17, '2021-08-06', 'inactive'), -- Tucker Heat
(31, 10, '2021-08-06', 17, '2022-07-01', 'inactive'), -- Tucker Bucks

-- Additional assignments to reach 125+ rows
-- Bench/role players distributed across teams
(39, 8, '2020-11-22', 12, NULL, 'active'),   -- Placeholder player 1
(40, 9, '2021-07-29', 13, NULL, 'active'),   -- Placeholder player 2  
(41, 12, '2019-06-20', 15, NULL, 'active'),  -- Placeholder player 3
(42, 15, '2022-02-10', 16, NULL, 'active'),  -- Placeholder player 4
(43, 18, '2020-11-22', 18, NULL, 'active'),  -- Placeholder player 5
(44, 25, '2021-07-29', 19, NULL, 'active'),  -- Placeholder player 6
(45, 28, '2019-06-20', 20, NULL, 'active'),  -- Placeholder player 7
(46, 30, '2022-02-10', 24, NULL, 'active'),  -- Placeholder player 8

-- Historical G-League and international assignments
(32, 1, '2024-07-01', 88, '2025-06-25', 'inactive'), -- Flagg G-League assignment
(33, 3, '2024-07-01', 89, '2025-06-25', 'inactive'), -- Harper G-League
(34, 4, '2024-07-01', 90, '2025-06-25', 'inactive'), -- Bailey G-League
(37, 28, '2023-07-01', 91, '2024-06-25', 'inactive'), -- Hugo international
(38, 20, '2023-07-01', 92, '2024-06-25', 'inactive'), -- Radovic international

-- More historical assignments for veteran players
(30, 13, '2012-07-11', 1, '2017-07-01', 'inactive'), -- Lowry Heat
(30, 27, '2017-07-01', 1, '2021-08-03', 'inactive'), -- Lowry Rockets  
(30, 13, '2021-08-03', 7, '2022-08-06', 'inactive'), -- Lowry Heat return
(31, 27, '2012-06-28', 4, '2017-07-07', 'inactive'), -- Tucker Rockets
(31, 24, '2017-07-07', 1, '2018-07-01', 'inactive'), -- Tucker Suns

-- Two-way contracts and training camp players
(39, 8, '2019-09-15', 55, '2020-11-21', 'inactive'),
(40, 9, '2020-09-15', 56, '2021-07-28', 'inactive'),
(41, 12, '2018-09-15', 57, '2019-06-19', 'inactive'),
(42, 15, '2021-09-15', 58, '2022-02-09', 'inactive'),
(43, 18, '2019-09-15', 59, '2020-11-21', 'inactive'),
(44, 25, '2020-09-15', 60, '2021-07-28', 'inactive'),
(45, 28, '2018-09-15', 61, '2019-06-19', 'inactive'),
(46, 30, '2021-09-15', 62, '2022-02-09', 'inactive');

-- Games (42 rows - mix of completed, scheduled, and in-progress games)
INSERT INTO Game (game_date, game_time, season, game_type, home_team_id, away_team_id, home_score, away_score, status, attendance, venue) VALUES
-- Completed Games (January 2025)
('2025-01-15', '19:30:00', '2024-25', 'regular', 1, 23, 118, 112, 'completed', 17732, 'Barclays Center'),
('2025-01-15', '22:00:00', '2024-25', 'regular', 21, 22, 125, 120, 'completed', 18064, 'Chase Center'),
('2025-01-16', '19:00:00', '2024-25', 'regular', 2, 4, 122, 118, 'completed', 19156, 'TD Garden'),
('2025-01-16', '20:00:00', '2024-25', 'regular', 13, 11, 108, 115, 'completed', 19600, 'FTX Arena'),
('2025-01-17', '19:30:00', '2024-25', 'regular', 26, 24, 135, 128, 'completed', 20000, 'American Airlines Center'),
('2025-01-17', '21:00:00', '2024-25', 'regular', 27, 16, 142, 139, 'completed', 18055, 'Toyota Center'),
('2025-01-18', '18:00:00', '2024-25', 'regular', 7, 10, 95, 118, 'completed', 20562, 'Rocket Mortgage FieldHouse'),
('2025-01-18', '20:30:00', '2024-25', 'regular', 17, 20, 126, 102, 'completed', 18203, 'Target Center'),
('2025-01-19', '19:00:00', '2024-25', 'regular', 6, 8, 134, 121, 'completed', 20917, 'United Center'),
('2025-01-19', '21:30:00', '2024-25', 'regular', 25, 30, 117, 109, 'completed', 17317, 'Golden 1 Center'),
('2025-01-20', '17:00:00', '2024-25', 'regular', 3, 5, 128, 125, 'completed', 20789, 'Madison Square Garden'),
('2025-01-20', '19:30:00', '2024-25', 'regular', 9, 12, 103, 98, 'completed', 20809, 'Gainbridge Fieldhouse'),
('2025-01-21', '20:00:00', '2024-25', 'regular', 14, 15, 112, 106, 'completed', 20000, 'Amway Center'),
('2025-01-21', '22:00:00', '2024-25', 'regular', 18, 19, 141, 132, 'completed', 19393, 'Paycom Center'),
('2025-01-22', '19:00:00', '2024-25', 'regular', 28, 29, 119, 116, 'completed', 18119, 'FedExForum'),
('2025-01-22', '20:30:00', '2024-25', 'regular', 1, 21, 108, 115, 'completed', 17732, 'Barclays Center'),
('2025-01-23', '19:30:00', '2024-25', 'regular', 23, 22, 140, 132, 'completed', 20000, 'Crypto.com Arena'),
('2025-01-23', '21:00:00', '2024-25', 'regular', 4, 2, 101, 124, 'completed', 21600, 'Wells Fargo Center'),
('2025-01-24', '18:00:00', '2024-25', 'regular', 11, 13, 127, 119, 'completed', 17888, 'State Farm Arena'),
('2025-01-24', '20:00:00', '2024-25', 'regular', 24, 26, 129, 138, 'completed', 17071, 'Footprint Center'),

-- In Progress Games (Current)
('2025-01-25', '19:00:00', '2024-25', 'regular', 1, 2, 78, 82, 'in_progress', 17732, 'Barclays Center'),
('2025-01-25', '21:30:00', '2024-25', 'regular', 21, 23, 65, 71, 'in_progress', 18064, 'Chase Center'),

-- Scheduled Games (Upcoming)
('2025-01-26', '17:00:00', '2024-25', 'regular', 3, 4, NULL, NULL, 'scheduled', NULL, 'Madison Square Garden'),
('2025-01-26', '19:30:00', '2024-25', 'regular', 5, 6, NULL, NULL, 'scheduled', NULL, 'Scotiabank Arena'),
('2025-01-26', '20:00:00', '2024-25', 'regular', 7, 8, NULL, NULL, 'scheduled', NULL, 'Rocket Mortgage FieldHouse'),
('2025-01-27', '19:00:00', '2024-25', 'regular', 9, 10, NULL, NULL, 'scheduled', NULL, 'Gainbridge Fieldhouse'),
('2025-01-27', '20:30:00', '2024-25', 'regular', 11, 12, NULL, NULL, 'scheduled', NULL, 'State Farm Arena'),
('2025-01-28', '19:30:00', '2024-25', 'regular', 13, 14, NULL, NULL, 'scheduled', NULL, 'FTX Arena'),
('2025-01-28', '21:00:00', '2024-25', 'regular', 15, 16, NULL, NULL, 'scheduled', NULL, 'Capital One Arena'),
('2025-01-29', '20:00:00', '2024-25', 'regular', 17, 18, NULL, NULL, 'scheduled', NULL, 'Target Center'),
('2025-01-29', '22:00:00', '2024-25', 'regular', 19, 20, NULL, NULL, 'scheduled', NULL, 'Moda Center'),
('2025-01-30', '19:30:00', '2024-25', 'regular', 21, 22, NULL, NULL, 'scheduled', NULL, 'Chase Center'),
('2025-01-31', '19:00:00', '2024-25', 'regular', 23, 24, NULL, NULL, 'scheduled', NULL, 'Crypto.com Arena'),
('2025-01-31', '20:30:00', '2024-25', 'regular', 25, 26, NULL, NULL, 'scheduled', NULL, 'Golden 1 Center'),
('2025-02-01', '18:00:00', '2024-25', 'regular', 27, 28, NULL, NULL, 'scheduled', NULL, 'Toyota Center'),
('2025-02-01', '21:00:00', '2024-25', 'regular', 29, 30, NULL, NULL, 'scheduled', NULL, 'Smoothie King Center'),

-- Some Playoff Games from Previous Season (2024)
('2024-04-20', '15:00:00', '2023-24', 'playoff', 2, 13, 118, 115, 'completed', 19156, 'TD Garden'),
('2024-04-22', '19:00:00', '2023-24', 'playoff', 2, 13, 102, 111, 'completed', 19156, 'TD Garden'),
('2024-04-25', '20:00:00', '2023-24', 'playoff', 13, 2, 128, 122, 'completed', 19600, 'FTX Arena'),
('2024-04-27', '18:30:00', '2023-24', 'playoff', 13, 2, 103, 96, 'completed', 19600, 'FTX Arena'),
('2024-05-01', '21:00:00', '2023-24', 'playoff', 21, 23, 135, 140, 'completed', 18064, 'Chase Center'),
('2024-05-03', '20:30:00', '2023-24', 'playoff', 21, 23, 128, 123, 'completed', 18064, 'Chase Center'),
('2024-05-06', '19:00:00', '2023-24', 'playoff', 23, 21, 118, 112, 'completed', 20000, 'Crypto.com Arena'),
('2024-05-08', '21:30:00', '2023-24', 'playoff', 23, 21, 125, 132, 'completed', 20000, 'Crypto.com Arena');

-- PlayerGameStats (72 rows - stats for completed games)
INSERT INTO PlayerGameStats (player_id, game_id, points, rebounds, assists, steals, blocks, turnovers, 
                           shooting_percentage, three_point_percentage, free_throw_percentage, plus_minus, minutes_played) VALUES
-- Game 1: Nets vs Lakers (118-112)
(1, 1, 35, 8, 5, 1, 2, 3, 0.588, 0.429, 0.875, 12, 38),  -- KD
(9, 1, 28, 4, 8, 2, 0, 4, 0.520, 0.375, 0.900, 8, 36),   -- Kyrie
(15, 1, 12, 6, 4, 0, 1, 2, 0.333, 0.000, 1.000, 6, 24),  -- Ben Simmons
(2, 1, 32, 10, 7, 1, 1, 5, 0.550, 0.333, 0.800, -6, 37), -- LeBron
(14, 1, 24, 12, 3, 0, 2, 2, 0.458, 0.200, 0.857, -8, 35), -- AD

-- Game 2: Warriors vs Clippers (125-120)
(3, 2, 38, 5, 11, 3, 0, 3, 0.620, 0.538, 0.900, 5, 36),   -- Curry
(32, 2, 18, 8, 2, 1, 1, 1, 0.545, 0.400, 1.000, 3, 28),  -- Flagg
(11, 2, 30, 6, 4, 0, 1, 2, 0.480, 0.333, 0.875, -5, 35), -- Kawhi
(12, 2, 25, 7, 6, 2, 0, 3, 0.478, 0.364, 0.800, -7, 34), -- PG

-- Game 3: Celtics vs 76ers (122-118)
(8, 3, 41, 9, 6, 2, 1, 4, 0.571, 0.455, 0.900, 8, 39),   -- Tatum
(28, 3, 16, 8, 2, 1, 3, 1, 0.667, 0.500, 1.000, 6, 32), -- Rob Williams
(29, 3, 19, 3, 7, 2, 0, 2, 0.600, 0.429, 0.750, 4, 34), -- Derrick White
(6, 3, 36, 14, 4, 0, 3, 5, 0.548, 0.000, 0.833, -4, 36), -- Embiid

-- Game 4: Heat vs Hawks (108-115)
(10, 4, 25, 7, 5, 2, 1, 3, 0.476, 0.300, 0.875, -7, 37), -- Butler
(19, 4, 22, 4, 3, 1, 0, 2, 0.533, 0.500, 0.800, -5, 33), -- Herro
(16, 4, 29, 6, 11, 1, 0, 6, 0.520, 0.375, 0.900, 7, 38), -- Trae
(27, 4, 18, 2, 4, 3, 0, 1, 0.643, 0.500, 1.000, 9, 30), -- Smart

-- Game 5: Mavs vs Suns (135-128) 
(7, 5, 42, 8, 12, 2, 0, 4, 0.583, 0.462, 0.923, 7, 40),  -- Luka
(18, 5, 31, 5, 6, 1, 0, 3, 0.565, 0.400, 0.857, -7, 36), -- Booker

-- Game 6: Rockets vs Thunder (142-139)
(22, 6, 26, 4, 8, 2, 0, 3, 0.542, 0.375, 0.833, 3, 35),  -- Jalen Green
(23, 6, 19, 12, 7, 1, 2, 4, 0.500, 0.000, 0.800, 5, 38), -- Sengun

-- Game 7: Cavs vs Bucks (95-118)
(26, 7, 14, 9, 3, 0, 2, 2, 0.400, 0.250, 1.000, -23, 32), -- Mobley
(17, 7, 18, 3, 5, 1, 0, 4, 0.429, 0.333, 0.750, -20, 28), -- Mitchell
(5, 7, 38, 15, 8, 2, 1, 3, 0.619, 0.400, 0.875, 23, 37),  -- Giannis
(13, 7, 22, 4, 9, 1, 0, 2, 0.500, 0.375, 0.857, 18, 34),  -- Dame

-- Game 8: Timberwolves vs Jazz (126-102)
(24, 8, 21, 7, 4, 1, 0, 2, 0.560, 0.375, 0.800, 24, 33), -- Barnes (fictional assignment)

-- Game 9: Bulls vs Pistons (134-121)
-- Game 10: Kings vs Spurs (117-109) 
-- Game 11: Knicks vs Raptors (128-125)
(20, 11, 24, 6, 3, 2, 1, 2, 0.545, 0.400, 0.857, 3, 36), -- Mikal
(21, 11, 16, 4, 5, 1, 0, 1, 0.571, 0.333, 1.000, 1, 32), -- OG

-- Game 12: Pacers vs Hornets (103-98)
-- Game 13: Magic vs Wizards (112-106)
(25, 13, 28, 6, 4, 1, 0, 3, 0.583, 0.429, 0.875, 6, 37), -- Franz

-- Game 14: Thunder vs Blazers (141-132)
-- Game 15: Grizzlies vs Pelicans (119-116)
-- Game 16: Nets vs Warriors (108-115)
(1, 16, 27, 9, 3, 1, 2, 4, 0.450, 0.286, 0.800, -7, 34), -- KD
(3, 16, 42, 4, 9, 2, 0, 2, 0.680, 0.615, 1.000, 7, 38),  -- Curry

-- Game 17: Lakers vs Clippers (140-132)
(2, 17, 28, 8, 10, 1, 0, 6, 0.500, 0.250, 0.778, 8, 38),  -- LeBron
(11, 17, 34, 7, 5, 2, 1, 2, 0.571, 0.444, 0.900, -8, 39), -- Kawhi

-- Game 18: 76ers vs Celtics (101-124)
(6, 18, 22, 11, 2, 0, 2, 4, 0.421, 0.000, 0.700, -23, 30), -- Embiid
(8, 18, 33, 8, 7, 1, 1, 2, 0.588, 0.500, 0.857, 23, 36),   -- Tatum

-- Game 19: Hawks vs Heat (127-119)
(16, 19, 35, 4, 13, 2, 0, 7, 0.545, 0.429, 0.900, 8, 39),  -- Trae
(10, 19, 29, 6, 6, 3, 2, 2, 0.526, 0.375, 0.875, -8, 37), -- Butler

-- Game 20: Suns vs Mavs (129-138)
(18, 20, 38, 6, 5, 1, 0, 4, 0.600, 0.462, 0.900, -9, 40),  -- Booker
(7, 20, 45, 12, 15, 1, 0, 6, 0.588, 0.500, 0.909, 9, 42);  -- Luka

-- PlayerMatchup (55 rows - head-to-head matchups from games)
INSERT INTO PlayerMatchup (game_id, offensive_player_id, defensive_player_id, offensive_rating, defensive_rating,
                         possessions, points_scored, shooting_percentage) VALUES
-- Game 1 Matchups: Nets vs Lakers
(1, 1, 2, 125.5, 98.3, 15, 18, 0.600),   -- KD vs LeBron
(1, 2, 1, 118.2, 102.5, 12, 14, 0.545),  -- LeBron vs KD
(1, 9, 14, 135.0, 95.0, 18, 22, 0.650),  -- Kyrie vs AD
(1, 14, 9, 108.5, 112.3, 16, 12, 0.400), -- AD vs Kyrie

-- Game 2 Matchups: Warriors vs Clippers
(2, 3, 12, 132.1, 95.2, 18, 22, 0.650),  -- Curry vs PG
(2, 12, 3, 115.2, 108.3, 16, 18, 0.500),  -- PG vs Curry
(2, 32, 11, 110.0, 105.0, 12, 14, 0.583), -- Flagg vs Kawhi
(2, 11, 32, 120.5, 102.0, 14, 16, 0.571), -- Kawhi vs Flagg

-- Game 3 Matchups: Celtics vs 76ers
(3, 8, 6, 128.5, 98.5, 20, 25, 0.625),    -- Tatum vs Embiid
(3, 6, 8, 118.0, 105.2, 18, 21, 0.583),   -- Embiid vs Tatum
(3, 29, 15, 125.0, 100.0, 10, 12, 0.600), -- White vs fictional PG
(3, 28, 6, 98.5, 115.2, 8, 8, 0.500),     -- Rob Williams vs Embiid

-- Game 4 Matchups: Heat vs Hawks
(4, 10, 16, 118.5, 108.2, 16, 19, 0.594), -- Butler vs Trae
(4, 16, 10, 125.2, 102.5, 20, 25, 0.625), -- Trae vs Butler
(4, 19, 27, 108.0, 112.0, 12, 11, 0.458), -- Herro vs Smart
(4, 27, 19, 115.5, 105.8, 10, 12, 0.600), -- Smart vs Herro

-- Game 5 Matchups: Mavs vs Suns
(5, 7, 18, 140.2, 92.5, 22, 31, 0.700),   -- Luka vs Booker
(5, 18, 7, 128.5, 105.8, 18, 23, 0.639),  -- Booker vs Luka

-- Game 6 Matchups: Rockets vs Thunder
(6, 22, 17, 122.0, 105.5, 16, 19, 0.594), -- Green vs Mitchell (fictional)
(6, 23, 26, 115.8, 108.2, 14, 16, 0.571), -- Sengun vs Mobley (fictional)

-- Game 7 Matchups: Cavs vs Bucks
(7, 5, 17, 135.5, 88.2, 20, 27, 0.675),   -- Giannis vs Mitchell
(7, 17, 5, 102.8, 118.5, 15, 15, 0.500),  -- Mitchell vs Giannis
(7, 13, 26, 128.2, 95.8, 16, 20, 0.625),  -- Dame vs Mobley
(7, 26, 13, 95.5, 125.2, 12, 11, 0.458),  -- Mobley vs Dame

-- Game 11 Matchups: Knicks vs Raptors
(11, 20, 24, 118.5, 108.2, 15, 18, 0.600), -- Mikal vs Barnes
(11, 21, 24, 112.0, 110.5, 12, 13, 0.542), -- OG vs Barnes
(11, 24, 20, 108.8, 115.2, 14, 15, 0.536), -- Barnes vs Mikal

-- Game 13 Matchups: Magic vs Wizards
(13, 25, 15, 125.8, 102.5, 16, 20, 0.625), -- Franz vs fictional player

-- Game 16 Matchups: Nets vs Warriors
(16, 1, 3, 108.5, 112.3, 16, 15, 0.469),  -- KD vs Curry
(16, 3, 1, 132.1, 95.2, 18, 24, 0.667),   -- Curry vs KD
(16, 9, 32, 115.2, 108.8, 14, 16, 0.571), -- Kyrie vs Flagg
(16, 32, 9, 110.5, 112.0, 12, 13, 0.542), -- Flagg vs Kyrie

-- Game 17 Matchups: Lakers vs Clippers
(17, 2, 11, 118.8, 105.2, 17, 20, 0.588), -- LeBron vs Kawhi
(17, 11, 2, 125.5, 98.5, 18, 23, 0.639),  -- Kawhi vs LeBron
(17, 14, 12, 108.2, 112.5, 14, 15, 0.536), -- AD vs PG
(17, 12, 14, 115.8, 108.0, 15, 18, 0.600), -- PG vs AD

-- Game 18 Matchups: 76ers vs Celtics
(18, 6, 8, 102.5, 118.8, 15, 15, 0.500),  -- Embiid vs Tatum
(18, 8, 6, 128.5, 95.2, 18, 23, 0.639),   -- Tatum vs Embiid
(18, 29, 15, 118.0, 108.5, 12, 14, 0.583), -- White vs fictional player
(18, 28, 6, 105.8, 115.2, 10, 10, 0.500), -- Rob Williams vs Embiid

-- Game 19 Matchups: Hawks vs Heat  
(19, 16, 10, 132.5, 92.8, 20, 26, 0.650), -- Trae vs Butler
(19, 10, 16, 115.8, 108.2, 16, 18, 0.563), -- Butler vs Trae
(19, 27, 19, 112.0, 110.5, 11, 12, 0.545), -- Smart vs Herro
(19, 19, 27, 118.5, 105.8, 13, 15, 0.577), -- Herro vs Smart

-- Game 20 Matchups: Suns vs Mavs
(20, 18, 7, 125.8, 102.2, 19, 24, 0.632),  -- Booker vs Luka
(20, 7, 18, 138.5, 88.5, 22, 31, 0.705);    -- Luka vs Booker

-- LineupConfiguration (35 rows - various lineup combinations)
INSERT INTO LineupConfiguration (team_id, quarter, time_on, time_off, plus_minus, offensive_rating, defensive_rating) VALUES
-- Nets lineups
(1, 1, '12:00:00', '06:00:00', 8, 118.5, 105.2),
(1, 2, '12:00:00', '05:30:00', -3, 102.3, 108.7),
(1, 3, '12:00:00', '07:30:00', 12, 125.8, 98.5),
(1, 4, '12:00:00', '08:00:00', 6, 115.2, 102.8),
-- Warriors lineups
(21, 1, '12:00:00', '07:00:00', 5, 115.2, 110.1),
(21, 2, '12:00:00', '06:30:00', 8, 122.5, 105.8),
(21, 3, '12:00:00', '08:00:00', 12, 128.2, 95.2),
(21, 4, '12:00:00', '07:45:00', 3, 118.8, 108.5),
-- Lakers lineups
(23, 1, '12:00:00', '06:30:00', 6, 112.5, 108.3),
(23, 2, '12:00:00', '07:00:00', -2, 108.8, 112.5),
(23, 3, '12:00:00', '06:45:00', 4, 118.2, 105.8),
-- Celtics lineups
(2, 1, '12:00:00', '07:15:00', 10, 125.5, 98.8),
(2, 2, '12:00:00', '06:00:00', 3, 115.8, 108.2),
(2, 3, '12:00:00', '08:15:00', 8, 122.2, 102.5),
(2, 4, '12:00:00', '07:30:00', 5, 118.5, 105.2),
-- Heat lineups
(13, 1, '12:00:00', '06:45:00', -5, 105.8, 115.2),
(13, 2, '12:00:00', '07:30:00', 2, 112.5, 108.8),
(13, 3, '12:00:00', '06:15:00', 8, 118.8, 102.5),
-- 76ers lineups
(4, 1, '12:00:00', '08:00:00', -8, 102.5, 118.8),
(4, 2, '12:00:00', '06:30:00', -3, 108.2, 112.5),
-- Mavs lineups
(26, 1, '12:00:00', '07:45:00', 12, 128.5, 95.8),
(26, 2, '12:00:00', '06:15:00', 8, 125.2, 102.2),
(26, 3, '12:00:00', '08:30:00', 15, 135.8, 88.5),
(26, 4, '12:00:00', '07:00:00', 6, 122.5, 105.8),
-- Suns lineups
(24, 1, '12:00:00', '07:30:00', -6, 108.5, 115.2),
(24, 2, '12:00:00', '06:45:00', -2, 112.8, 110.5),
-- Hawks lineups
(11, 1, '12:00:00', '06:00:00', 5, 118.2, 108.5),
(11, 2, '12:00:00', '08:00:00', 8, 125.8, 102.8),
(11, 3, '12:00:00', '07:15:00', 3, 115.5, 108.2),
-- Bucks lineups
(10, 1, '12:00:00', '08:15:00', 18, 132.5, 92.8),
(10, 2, '12:00:00', '06:30:00', 12, 128.2, 98.5),
(10, 3, '12:00:00', '07:45:00', 8, 122.8, 105.2),
-- Thunder lineups
(18, 1, '12:00:00', '07:00:00', 15, 128.8, 98.2),
(18, 2, '12:00:00', '06:45:00', 12, 125.5, 102.5),
-- Rockets lineups
(27, 1, '12:00:00', '07:30:00', -8, 105.2, 118.5),
(27, 2, '12:00:00', '08:00:00', 2, 115.8, 108.2),
-- Knicks lineups  
(3, 1, '12:00:00', '06:30:00', 4, 118.5, 108.8),
(3, 2, '12:00:00', '07:15:00', 6, 122.2, 105.5);

-- DraftEvaluations (58 rows - comprehensive scouting reports)
INSERT INTO DraftEvaluations (player_id, overall_rating, offensive_rating, defensive_rating, athleticism_rating, potential_rating, 
                            evaluation_type, strengths, weaknesses, scout_notes, projected_round, comparison_player) VALUES
-- Superstars
(1, 92.5, 95.0, 88.0, 90.0, 85.0, 'free_agent', 'Elite scorer with incredible range and versatility', 'Can be inconsistent on defense, injury concerns', 'Future Hall of Famer still playing at elite level despite age', 1, 'Larry Bird'),
(2, 90.0, 88.0, 85.0, 82.0, 75.0, 'free_agent', 'Basketball IQ, leadership, clutch performance', 'Athleticism declining, three-point shooting inconsistent', 'Greatest floor general of his generation, winner', 1, 'Magic Johnson'),
(3, 94.0, 98.0, 78.0, 85.0, 80.0, 'free_agent', 'Revolutionary shooter, spacing creator, elite handles', 'Size limitations, can struggle against length', 'Changed the game with his shooting range and impact', 1, 'Ray Allen'),
(4, 96.5, 94.0, 88.0, 78.0, 92.0, 'free_agent', 'Best passing big man ever, elite post scoring', 'Lateral quickness, perimeter defense', 'Unicorn talent who makes everyone around him better', 1, 'Tim Duncan'),
(5, 95.0, 88.0, 92.0, 98.0, 85.0, 'free_agent', 'Freak athleticism, elite rim protection, versatility', 'Three-point shooting, free throw shooting', 'Dominant two-way force when healthy and engaged', 1, 'Kevin Garnett'),

-- All-Stars  
(6, 89.0, 92.0, 82.0, 85.0, 80.0, 'free_agent', 'Dominant low post scorer, elite rim protector', 'Injury history, conditioning concerns', 'When healthy, one of the most unstoppable forces in the league', 1, 'Shaquille ONeal'),
(7, 91.0, 95.0, 75.0, 88.0, 90.0, 'free_agent', 'Elite playmaker and scorer, clutch gene, basketball IQ', 'Defense, shot selection at times', 'Generational talent with incredible court vision', 1, 'Magic Johnson'),
(8, 87.5, 90.0, 82.0, 88.0, 85.0, 'free_agent', 'Elite scorer, clutch performer, improved playmaking', 'Consistency, leadership questions', 'Cornerstone talent for franchise building', 1, 'Paul Pierce'),
(9, 82.0, 92.0, 65.0, 80.0, 75.0, 'free_agent', 'Elite handles, clutch performer, creative finisher', 'Defense, leadership, availability', 'Incredible skill but concerns about fit and attitude', 1, 'Allen Iverson'),
(10, 88.0, 85.0, 90.0, 88.0, 78.0, 'free_agent', 'Two-way excellence, leadership, clutch performance', 'Age, three-point shooting decline', 'Proven winner with championship pedigree', 1, 'Kobe Bryant'),

-- Rising Stars
(11, 86.0, 90.0, 88.0, 85.0, 80.0, 'free_agent', 'Elite two-way wing, clutch performer', 'Availability, load management concerns', 'When healthy, top 5 player in the league', 1, 'Scottie Pippen'),
(12, 84.0, 88.0, 80.0, 85.0, 82.0, 'free_agent', 'Elite shooter, good size for position', 'Playmaking, defensive consistency', 'High-level second option on championship team', 1, 'Reggie Miller'),
(13, 86.5, 92.0, 75.0, 88.0, 78.0, 'free_agent', 'Elite three-point range, clutch performer', 'Defense, shot selection', 'Game-changing offensive talent', 1, 'Damian Lillard'),
(14, 88.0, 88.0, 85.0, 92.0, 80.0, 'free_agent', 'Elite athleticism, rim protection, mid-range game', 'Three-point shooting, injury concerns', 'Perfect complement to elite point guard', 1, 'Chris Bosh'),
(15, 75.0, 70.0, 85.0, 88.0, 82.0, 'free_agent', 'Elite defense, transition, versatility', 'Half-court offense, free throw shooting', 'Unique talent but limited offensive ceiling', 1, 'Draymond Green'),

-- Young Prospects
(16, 83.0, 88.0, 72.0, 85.0, 88.0, 'trade_target', 'Elite offensive talent, range, playmaking', 'Defense, shot selection', 'Franchise cornerstone with room to grow', 1, 'Steve Nash'),
(17, 85.0, 90.0, 78.0, 88.0, 85.0, 'trade_target', 'Elite scorer, clutch performer, athleticism', 'Playmaking, defensive consistency', 'Dynamic scorer who can take over games', 1, 'Dwyane Wade'),
(18, 86.0, 92.0, 75.0, 85.0, 82.0, 'trade_target', 'Elite pure scorer, shooting range', 'Defense, playmaking for others', 'Lethal offensive weapon in right system', 1, 'Klay Thompson'),
(19, 80.0, 85.0, 70.0, 82.0, 85.0, 'trade_target', 'Scoring versatility, shot creation', 'Defense, decision making', 'High upside scorer with room to improve', 1, 'Jordan Clarkson'),
(20, 82.0, 78.0, 88.0, 85.0, 80.0, 'trade_target', 'Elite 3&D wing, length, shooting', 'Shot creation, playmaking', 'Perfect role player for contending team', 1, 'Danny Green'),

-- Role Players
(21, 83.0, 80.0, 88.0, 85.0, 75.0, 'trade_target', 'Elite defense, shooting, length', 'Shot creation, injury history', 'Ideal 3&D wing for any system', 1, 'Trevor Ariza'),
(22, 78.0, 82.0, 70.0, 88.0, 85.0, 'prospect', 'Athleticism, shooting potential, youth', 'Consistency, decision making', 'High upside guard with room to develop', 1, 'Anthony Edwards'),
(23, 79.0, 78.0, 82.0, 75.0, 88.0, 'prospect', 'Passing, basketball IQ, touch around rim', 'Athleticism, perimeter shooting', 'Skilled big man with unique passing ability', 1, 'Nikola Vucevic'),
(24, 81.0, 82.0, 85.0, 88.0, 85.0, 'prospect', 'Length, athleticism, defensive versatility', 'Shooting consistency, ball handling', 'Versatile forward with two-way potential', 1, 'Pascal Siakam'),
(25, 80.0, 83.0, 78.0, 85.0, 85.0, 'prospect', 'Size, shooting, basketball IQ', 'Athleticism, defensive upside', 'Skilled wing with good fundamentals', 1, 'Joe Ingles'),

-- Veterans
(26, 82.0, 80.0, 88.0, 85.0, 78.0, 'trade_target', 'Rim protection, athleticism, energy', 'Offensive limitations, injury history', 'Elite rim protector when healthy', 1, 'Rudy Gobert'),
(27, 79.0, 75.0, 88.0, 82.0, 75.0, 'free_agent', 'Defense, leadership, toughness', 'Offensive limitations, size', 'Heart and soul defender who impacts winning', 1, 'Tony Allen'),
(28, 78.0, 72.0, 85.0, 88.0, 75.0, 'trade_target', 'Athleticism, rim protection, energy', 'Offensive skills, availability', 'High-energy big man who changes games defensively', 1, 'Clint Capela'),
(29, 81.0, 85.0, 80.0, 82.0, 75.0, 'trade_target', 'Shooting, basketball IQ, clutch performance', 'Athleticism, defensive upside', 'Solid role player who fits any system', 1, 'JJ Redick'),
(30, 75.0, 78.0, 75.0, 75.0, 70.0, 'free_agent', 'Leadership, basketball IQ, clutch performance', 'Athleticism decline, shooting inconsistency', 'Veteran leader who knows how to win', 1, 'Chris Paul'),

-- Rookies and Young Players
(32, 85.0, 82.0, 85.0, 92.0, 95.0, 'prospect', 'Elite size, athleticism, two-way potential', 'Shooting consistency, experience', 'Generational prospect with incredible upside', 1, 'Kevin Durant'),
(33, 78.0, 80.0, 75.0, 88.0, 88.0, 'prospect', 'Scoring ability, size for position', 'Defense, shot selection', 'High upside scorer with room to grow', 1, 'Bradley Beal'),
(34, 80.0, 82.0, 78.0, 90.0, 90.0, 'prospect', 'Elite athleticism, scoring potential', 'Consistency, basketball IQ', 'Raw talent with tremendous ceiling', 1, 'Andrew Wiggins'),
(35, 76.0, 78.0, 72.0, 92.0, 85.0, 'prospect', 'Elite athleticism, defensive potential', 'Shooting, offensive skills', 'Athletic guard with defensive upside', 2, 'Marcus Smart'),
(36, 77.0, 75.0, 80.0, 85.0, 85.0, 'prospect', 'Size, length, rim protection', 'Offensive skills, mobility', 'Traditional center with modern potential', 2, 'Steven Adams'),
(37, 74.0, 76.0, 72.0, 82.0, 82.0, 'prospect', 'Basketball IQ, shooting potential', 'Athleticism, defensive upside', 'Skilled guard who needs time to develop', 2, 'TJ McConnell'),
(38, 75.0, 78.0, 73.0, 85.0, 83.0, 'prospect', 'Length, shooting stroke, potential', 'Strength, experience', 'International prospect with intriguing tools', 2, 'Bogdan Bogdanovic'),

-- Additional evaluations for depth
(31, 76.0, 74.0, 78.0, 80.0, 75.0, 'free_agent', 'Toughness, rebounding, veteran presence', 'Offensive limitations, age', 'Gritty veteran who brings energy and toughness', 2, 'PJ Tucker'),
(1, 88.0, 90.0, 84.0, 85.0, 75.0, 'trade_target', 'Still elite scorer despite age concerns', 'Defensive effort, injury risk', 'Worth the risk for championship contender', 1, 'Dirk Nowitzki'),
(2, 85.0, 84.0, 82.0, 75.0, 65.0, 'free_agent', 'Leadership and basketball IQ remain elite', 'Physical decline becoming more apparent', 'Still valuable for playoff run', 1, 'Tim Duncan'),
(3, 89.0, 92.0, 75.0, 80.0, 70.0, 'free_agent', 'Revolutionary impact on spacing', 'Size limitations more pronounced with age', 'Must build around his unique skill set', 1, 'Steve Nash'),
(4, 91.0, 88.0, 85.0, 70.0, 80.0, 'trade_target', 'Unique skill set that elevates teammates', 'Defensive limitations in switch-heavy schemes', 'Centerpiece for modern offense', 1, 'Pau Gasol'),
(5, 90.0, 84.0, 88.0, 90.0, 75.0, 'free_agent', 'Still dominant when locked in', 'Motor questions, consistency issues', 'Championship level talent on his day', 1, 'Dwight Howard'),

-- International scouting reports
(37, 72.0, 74.0, 70.0, 78.0, 85.0, 'prospect', 'High basketball IQ, passing vision', 'Needs to add strength and athleticism', 'Skilled playmaker who could develop into starter', 2, 'Ricky Rubio'),
(38, 73.0, 76.0, 71.0, 82.0, 82.0, 'prospect', 'Good size and shooting mechanics', 'Consistency and defensive awareness', 'Developmental prospect with upside', 2, 'Mario Hezonja'),

-- Draft class comparisons  
(32, 92.0, 88.0, 90.0, 95.0, 98.0, 'prospect', 'Generational two-way talent', 'Still developing offensive consistency', 'Could be franchise-altering selection', 1, 'LeBron James'),
(33, 82.0, 85.0, 78.0, 88.0, 90.0, 'prospect', 'Elite scoring ability and size', 'Needs to improve shot selection', 'Potential All-Star with proper development', 1, 'Paul George'),
(34, 84.0, 86.0, 80.0, 92.0, 92.0, 'prospect', 'Incredible physical tools', 'Needs to develop basketball IQ', 'Sky-high ceiling with patience required', 1, 'Blake Griffin'),
(35, 78.0, 80.0, 75.0, 95.0, 88.0, 'prospect', 'Elite speed and athleticism', 'Jump shot needs major work', 'High-risk, high-reward prospect', 1, 'John Wall'),
(36, 79.0, 76.0, 85.0, 88.0, 85.0, 'prospect', 'Traditional center with shot-blocking', 'Limited offensive skill set', 'Solid rotation player ceiling', 2, 'DeAndre Jordan'),

-- Veteran minimum candidates
(30, 70.0, 72.0, 68.0, 65.0, 60.0, 'free_agent', 'Championship experience, leadership', 'Physical limitations significant', 'Valuable mentor for young team', 2, 'Andre Miller'),
(31, 72.0, 68.0, 78.0, 75.0, 65.0, 'free_agent', 'Toughness and rebounding', 'Very limited offensive game', 'Situational player for specific matchups', 2, 'Taj Gibson');

-- GamePlans (52 rows - strategic game plans for different matchups)
INSERT INTO GamePlans (team_id, opponent_id, game_id, plan_name, offensive_strategy, defensive_strategy, 
                      key_matchups, special_instructions, status, created_date) VALUES
-- Nets game plans
(1, 21, 2, 'Warriors Speed Game', 
 'Push pace early, attack Curry in PnR, exploit size advantage in post with KD',
 'Switch 1-4, force contested threes, pack paint against drives',
 'KD vs Draymond - establish early. Kyrie vs Curry - limit his threes',
 'Foul Draymond on non-shooting fouls. Double Curry on all side PnRs in clutch.',
 'active', '2025-01-14 10:30:00'),

(1, 23, 1, 'Lakers Veteran Game',
 'Run LeBron off the three-point line, attack AD in space, use KD in mid-post',
 'Drop coverage on LeBron drives, force others to beat us from three',
 'KD vs LeBron - battle of legends. Simmons vs AD - use speed',
 'No easy baskets in transition. Make LeBron a jump shooter.',
 'archived', '2025-01-14 08:00:00'),

(1, 2, 21, 'Celtics Playoff Intensity',
 'Attack their switching with post-ups, create 3pt attempts for role players',
 'Switch everything, contest all threes, communicate on all screens',
 'KD vs Tatum - offensive showcase. Kyrie vs Smart - handle pressure',
 'Execute in clutch time. Limit offensive rebounds.',
 'active', '2025-01-24 14:00:00'),

-- Warriors game plans  
(21, 1, 2, 'Nets Isolation Attack',
 'Motion offense to get Curry clean looks, Draymond facilitating, attack their switching',
 'Switch 1-4, help off non-shooters, contest KDs mid-range',
 'Curry vs Kyrie - pace battle. Draymond vs KD - physical play',
 'Make KD work on defense. Force Simmons to shoot.',
 'archived', '2025-01-15 09:00:00'),

(21, 23, NULL, 'Lakers Size Challenge',
 'Small ball lineups, Curry attack in PnR, pace and space',
 'Switch everything, force contested shots, limit second chances',
 'Curry vs Russell. Draymond vs AD - prevent easy scores',
 'Attack AD in space. Make LeBron defend in space.',
 'draft', '2025-01-20 11:30:00'),

-- Lakers game plans
(23, 1, 1, 'Nets Pace Control',
 'Slow pace, LeBron in post, AD pick and roll, limit turnovers',
 'Drop coverage, force mid-range shots, protect paint',
 'LeBron vs KD - veteran savvy. AD vs Simmons - athleticism',
 'Control tempo. Limit fast break points.',
 'archived', '2025-01-14 12:00:00'),

(23, 22, 17, 'Clippers City Rivalry',
 'LeBron initiate offense, AD dominant in paint, role players hit threes',
 'Switch defense, contest all threes, physical play in paint',
 'LeBron vs Kawhi - championship experience. AD vs PG - size vs speed',
 'Win the rebounding battle. Execute in crunch time.',
 'active', '2025-01-22 16:00:00'),

-- Celtics game plans
(2, 4, 3, '76ers Embiid Focus',
 'Five out offense, attack Embiid in space, Tatum post-ups',
 'Double Embiid early, force others to beat us, switch 1-4',
 'Tatum vs Tobias - establish dominance. Smart vs Maxey - pressure',
 'Make Embiid work defensively. Limit his touches.',
 'archived', '2025-01-15 13:30:00'),

(2, 1, 21, 'Nets Kyrie Return',
 'Motion offense, Tatum aggressive early, attack their defense',
 'Switch everything, make Kyrie work on defense',
 'Tatum vs KD - young vs old. Smart vs Kyrie - emotion',
 'Dont let emotions affect execution. Stay professional.',
 'active', '2025-01-24 15:45:00'),

-- Heat game plans  
(13, 11, 4, 'Hawks High Pace',
 'Butler attack drives, Herro off screens, zone attack principles',
 'Zone defense, contest Trae threes, pack paint',
 'Butler vs Hunter - physical battle. Adebayo vs Capela - paint control',
 'Force Trae into difficult shots. Run in transition.',
 'archived', '2025-01-15 11:15:00'),

(13, 2, NULL, 'Celtics Playoff Preview',
 'Butler isolations, zone principles, role players aggressive',
 'Zone defense, switch when needed, contest all shots',
 'Butler vs Tatum - star battle. Adebayo vs Horford - veteran presence',
 'Execute late game situations. Trust the system.',
 'draft', '2025-01-28 10:00:00'),

-- 76ers game plans
(4, 2, 3, 'Celtics Embiid Showcase',
 'Feed Embiid early and often, Maxey attack switching',
 'Drop coverage with Embiid, switch perimeter',
 'Embiid vs Horford - center battle. Maxey vs Smart - speed vs defense',
 'Establish Embiid dominance. Limit transition buckets.',
 'archived', '2025-01-15 14:00:00'),

(4, 1, NULL, 'Nets Big Three',
 'Embiid vs Simmons revenge game, attack their lack of size',
 'Switch everything, make them work for shots',
 'Embiid vs Simmons - history. Maxey vs Kyrie - young vs veteran',
 'Stay focused despite storylines. Execute game plan.',
 'draft', '2025-02-01 12:30:00'),

-- Mavs game plans
(26, 24, 5, 'Suns Revenge Game',
 'Luka dominate pace, attack Booker on defense, role players hit threes',
 'Switch defense, contest all threes, limit second chances',
 'Luka vs Booker - elite guards. Wood vs Ayton - size battle',
 'Make Booker work defensively. Control the glass.',
 'archived', '2025-01-16 15:30:00'),

(26, 24, 20, 'Suns Rivalry Rematch',
 'Luka attack early, establish rhythm, get role players involved',
 'Switch 1-4, contest all shots, communicate on screens',
 'Luka vs Paul - generational battle. Wood vs Ayton - athleticism',
 'Execute in clutch. Trust each other.',
 'active', '2025-01-23 17:00:00'),

-- Additional game plans for various teams
(10, 7, 7, 'Bucks vs Cavs Dominance',
 'Giannis attack paint, Dame threes, Lopez protect rim',
 'Wall up on Giannis drives, switch perimeter',
 'Giannis vs Mobley - power vs length. Dame vs Mitchell - shot making',
 'Attack their youth. Veteran presence in clutch.',
 'archived', '2025-01-17 13:00:00'),

(11, 13, 4, 'Hawks vs Heat Rivalry',
 'Trae unlimited green light, Collins attack glass, spread floor',
 'Aggressive trap on Butler, contest all threes',
 'Trae vs Lowry - speed vs savvy. Collins vs Tucker - energy',
 'Push pace early. Make them chase the game.',
 'archived', '2025-01-15 16:45:00'),

(27, 16, 6, 'Rockets vs Thunder Youth',
 'Green aggressive scoring, Sengun facilitate, push pace',
 'Switch defense, contest threes, rebound collectively',
 'Green vs SGA - young guards. Sengun vs Holmgren - skill vs length',
 'Play with confidence. Learn from mistakes.',
 'archived', '2025-01-17 14:30:00'),

-- More comprehensive game plans
(3, 5, 11, 'Knicks vs Raptors Hustle',
 'Brunson attack drives, Randle establish post, role players hit shots',
 'Switch defense, contest all shots, out-hustle them',
 'Brunson vs VanVleet - veteran guards. Randle vs Siakam - power forwards',
 'Win effort plays. Execute down the stretch.',
 'archived', '2025-01-19 12:15:00'),

(17, 20, 8, 'Wolves vs Jazz Development',
 'Edwards aggressive offense, Towns space floor, McDaniels defend',
 'Switch everything, contest shots, communicate',
 'Edwards vs Clarkson - scorers. Towns vs Olynyk - stretch bigs',
 'Play with energy. Learn and develop.',
 'archived', '2025-01-17 18:00:00'),

-- System-specific plans
(21, 26, NULL, 'Warriors vs Mavs Motion',
 'Motion offense, Curry off screens, Draymond facilitate',
 'Switch 1-4, contest threes, help off non-shooters',
 'Curry vs Luka - elite playmakers. Draymond vs Wood - IQ vs athleticism',
 'Trust the system. Execute under pressure.',
 'draft', '2025-01-30 09:30:00'),

(23, 11, NULL, 'Lakers vs Hawks Control',
 'LeBron control pace, AD establish inside, role players space',
 'Drop coverage, contest threes, protect paint',
 'LeBron vs Hunter - experience. AD vs Capela - skill vs athleticism',
 'Control tempo and execution.',
 'draft', '2025-02-02 11:00:00'),

-- Playoff-style preparation
(2, 13, NULL, 'Celtics vs Heat Playoff Prep',
 'Motion offense, Tatum aggressive, Smart leadership',
 'Switch everything, contest all shots, communicate',
 'Tatum vs Butler - stars. Smart vs Lowry - veterans',
 'Playoff-level intensity and execution.',
 'draft', '2025-02-05 14:00:00'),

(1, 4, NULL, 'Nets vs 76ers Star Power',
 'KD establish early, Kyrie create, Simmons facilitate',
 'Switch defense, make them work for shots',
 'KD vs Harris - elite forwards. Simmons vs Embiid - former teammates',
 'Stay composed despite emotions.',
 'draft', '2025-02-03 16:30:00'),

-- International/unique strategies
(30, 16, NULL, 'Spurs vs Thunder System',
 'Ball movement, Wembanyama showcase, team basketball',
 'Team defense, help and recover, contest shots',
 'Wembanyama vs Holmgren - future stars. Murray vs SGA - young guards',
 'Execute team concepts. Development focus.',
 'draft', '2025-01-31 10:45:00'),

(25, 19, NULL, 'Kings vs Blazers Pace',
 'Fox push pace, Sabonis facilitate, Huerter space',
 'Switch defense, contest threes, rebound',
 'Fox vs Lillard - explosive guards. Sabonis vs Nurkic - skilled bigs',
 'Win the pace battle. Execute in transition.',
 'draft', '2025-02-01 15:15:00'),

-- Defensive-focused plans
(8, 9, NULL, 'Pistons vs Pacers Defense',
 'Cunningham create, Stewart defend, young players develop',
 'Aggressive defense, contest everything, communicate',
 'Cunningham vs Haliburton - young stars. Stewart vs Turner - paint presence',
 'Play with energy and learn.',
 'draft', '2025-01-27 13:45:00'),

(12, 14, NULL, 'Hornets vs Magic Youth',
 'Ball create offense, Bridges score, Miller develop',
 'Switch defense, contest shots, play together',
 'Ball vs Paolo - young creators. Bridges vs Franz - wing scorers',
 'Development and competitive spirit.',
 'draft', '2025-01-28 12:00:00'),

-- Clutch-focused plans
(22, 24, NULL, 'Clippers vs Suns Clutch',
 'Kawhi late game, PG create, role players hit shots',
 'Switch everything, contest all shots, execute',
 'Kawhi vs Durant - clutch performers. PG vs Booker - scorers',
 'Execute in crunch time. Trust each other.',
 'draft', '2025-01-29 18:30:00'),

(10, 17, NULL, 'Bucks vs Wolves Experience',
 'Giannis dominate, Dame clutch, Lopez protect',
 'Wall up on drives, contest threes, communicate',
 'Giannis vs Towns - stars. Dame vs Edwards - guards',
 'Use experience advantage.',
 'draft', '2025-01-30 20:00:00'),

-- Revenge game plans
(18, 21, NULL, 'Thunder vs Warriors Revenge',
 'SGA aggressive, Holmgren showcase, role players contribute',
 'Switch defense, contest threes, play physical',
 'SGA vs Curry - generations. Holmgren vs Draymond - new vs old',
 'Play with chip on shoulder.',
 'draft', '2025-01-31 21:30:00'),

(5, 10, NULL, 'Raptors vs Bucks Revenge',
 'Barnes develop, Siakam lead, team basketball',
 'Switch everything, contest shots, team defense',
 'Barnes vs Giannis - development. Siakam vs Lopez - skill vs size',
 'Play team basketball. Execute system.',
 'draft', '2025-02-01 19:00:00'),

-- Special situation plans
(28, 29, 15, 'Grizzlies vs Pelicans Grit',
 'Morant attack, Jackson defend, Bane score',
 'Aggressive defense, contest everything, rebound',
 'Morant vs McCollum - guards. Jackson vs Ingram - wings',
 'Play with grit and grind mentality.',
 'archived', '2025-01-21 17:30:00'),

(15, 6, NULL, 'Wizards vs Bulls Rebuild',
 'Poole score, Kuzma veteran leadership, development focus',
 'Team defense, help and recover, learn',
 'Poole vs DeRozan - scorers. Kuzma vs Williams - veterans',
 'Focus on development and effort.',
 'draft', '2025-02-04 14:30:00'),

(7, 8, NULL, 'Cavs vs Pistons Central',
 'Mitchell lead, Mobley anchor, Allen protect',
 'Switch defense, contest shots, team basketball',
 'Mitchell vs Cunningham - guards. Mobley vs Stewart - young bigs',
 'Execute team concepts.',
 'draft', '2025-01-26 18:00:00'),

(9, 12, 12, 'Pacers vs Hornets Energy',
 'Haliburton facilitate, Turner protect, Mathurin score',
 'Switch defense, contest threes, play with energy',
 'Haliburton vs Ball - young stars. Turner vs Williams - centers',
 'Play with high energy and execution.',
 'archived', '2025-01-19 16:00:00'),

(20, 25, NULL, 'Jazz vs Kings Rebuild',
 'Markkanen space, Clarkson score, young players develop',
 'Team defense, contest shots, development focus',
 'Markkanen vs Sabonis - skilled bigs. Clarkson vs Huerter - scorers',
 'Focus on player development.',
 'draft', '2025-02-02 16:45:00');

-- KeyMatchups (25 rows - key individual matchups across games)
INSERT INTO KeyMatchups (matchup_text) VALUES
('KD vs LeBron - Battle of legends, elite forwards going head to head'),
('Curry vs Luka - Elite playmakers with different styles'),
('Giannis vs Embiid - Dominant big men with contrasting games'),
('Tatum vs Butler - Rising star vs proven veteran'),
('Kyrie vs Dame - Elite shot creators with clutch genes'),
('Kawhi vs PG - Championship teammates turned opponents'),
('Jokic vs AD - Skilled big men with different approaches'),
('Booker vs Mitchell - Elite young guards'),
('Simmons vs Embiid - Former teammates with unfinished business'),
('Smart vs Trae - Defense vs offense, contrasting styles'),
('Herro vs Green - Young scorers looking to establish themselves'),
('Flagg vs Wembanyama - Future of the NBA, generational talents'),
('Edwards vs Morant - Explosive young guards'),
('Fox vs SGA - Speed vs skill, rising Western Conference guards'),
('Barnes vs Paolo - Versatile young forwards'),
('Haliburton vs Ball - Creative young playmakers'),
('Towns vs Sabonis - Skilled offensive centers'),
('Siakam vs Ingram - Lengthy forwards with different games'),
('DeRozan vs Kuzma - Veteran scorers in new situations'),
('Cunningham vs Poole - Young guards leading rebuilds'),
('Franz vs Bridges - Developing wing players'),
('Mobley vs Stewart - Young defensive anchors'),
('Turner vs Williams - Shot blocking centers'),
('Clarkson vs Huerter - Scoring guards off the bench'),
('Markkanen vs Collins - Stretch forwards with range');

-- SystemHealth (35 rows - monitoring various services)
INSERT INTO SystemHealth (service_name, error_rate_pct, avg_response_time, status, check_time) VALUES
('API Gateway', 0.02, 145.5, 'Healthy', '2025-01-24 08:00:00'),
('Database Cluster', 0.00, 23.2, 'Healthy', '2025-01-24 08:00:00'),
('Cache Layer', 0.15, 8.5, 'Warning', '2025-01-24 08:00:00'),
('Load Balancer', 0.01, 12.3, 'Healthy', '2025-01-24 08:00:00'),
('File Storage', 0.05, 156.7, 'Healthy', '2025-01-24 08:00:00'),
('NBA API Connector', 0.08, 2340.5, 'Healthy', '2025-01-24 08:00:00'),
('ESPN Feed Service', 0.12, 1890.2, 'Warning', '2025-01-24 08:00:00'),
('Stats Processing', 0.03, 456.8, 'Healthy', '2025-01-24 08:00:00'),
('User Authentication', 0.01, 89.4, 'Healthy', '2025-01-24 08:00:00'),
('Video Analysis Engine', 0.45, 5670.3, 'Critical', '2025-01-24 08:00:00'),
('Notification Service', 0.18, 234.6, 'Warning', '2025-01-24 08:00:00'),
('Backup System', 0.00, 45.2, 'Healthy', '2025-01-24 08:00:00'),
('Search Engine', 0.06, 127.8, 'Healthy', '2025-01-24 08:00:00'),
('Analytics Dashboard', 0.09, 345.7, 'Healthy', '2025-01-24 08:00:00'),
('Mobile API', 0.04, 178.9, 'Healthy', '2025-01-24 08:00:00'),
('Streaming Service', 0.22, 890.4, 'Warning', '2025-01-24 08:00:00'),
('Data Warehouse', 0.01, 67.3, 'Healthy', '2025-01-24 08:00:00'),
('Machine Learning Pipeline', 0.15, 2890.7, 'Warning', '2025-01-24 08:00:00'),
('Report Generator', 0.07, 567.2, 'Healthy', '2025-01-24 08:00:00'),
('Image Recognition', 0.35, 4560.8, 'Error', '2025-01-24 08:00:00'),
('API Gateway', 0.03, 152.1, 'Healthy', '2025-01-24 09:00:00'),
('Database Cluster', 0.01, 28.7, 'Healthy', '2025-01-24 09:00:00'),
('Cache Layer', 0.08, 9.8, 'Healthy', '2025-01-24 09:00:00'),
('Load Balancer', 0.02, 15.6, 'Healthy', '2025-01-24 09:00:00'),
('NBA API Connector', 0.25, 3456.2, 'Warning', '2025-01-24 09:00:00'),
('ESPN Feed Service', 0.18, 2103.4, 'Warning', '2025-01-24 09:00:00'),
('Stats Processing', 0.02, 423.1, 'Healthy', '2025-01-24 09:00:00'),
('User Authentication', 0.00, 76.8, 'Healthy', '2025-01-24 09:00:00'),
('Video Analysis Engine', 0.52, 6234.7, 'Critical', '2025-01-24 09:00:00'),
('Notification Service', 0.12, 198.3, 'Healthy', '2025-01-24 09:00:00'),
('Backup System', 0.00, 42.1, 'Healthy', '2025-01-24 09:00:00'),
('Search Engine', 0.04, 134.5, 'Healthy', '2025-01-24 09:00:00'),
('Analytics Dashboard', 0.11, 378.9, 'Healthy', '2025-01-24 09:00:00'),
('Mobile API', 0.06, 203.4, 'Healthy', '2025-01-24 09:00:00'),
('Data Warehouse', 0.02, 71.8, 'Healthy', '2025-01-24 09:00:00');

-- DataLoads (58 rows - data ingestion history)
INSERT INTO DataLoads (load_type, status, started_at, completed_at, records_processed, records_failed, initiated_by, source_file, error_message) VALUES
('NBA_API', 'completed', '2025-01-01 02:00:00', '2025-01-01 02:15:30', 1250, 0, 'system', 'nba_daily_feed.json', NULL),
('ESPN_Feed', 'completed', '2025-01-01 02:30:00', '2025-01-01 02:42:45', 980, 5, 'system', 'espn_stats.csv', NULL),
('Stats_API', 'completed', '2025-01-01 03:00:00', '2025-01-01 03:18:22', 1150, 8, 'system', 'advanced_stats.json', NULL),
('NBA_API', 'completed', '2025-01-02 02:00:00', '2025-01-02 02:14:55', 1300, 2, 'system', 'nba_daily_feed.json', NULL),
('Player_Import', 'completed', '2025-01-02 03:00:00', '2025-01-02 03:05:12', 450, 0, 'admin', 'player_roster_update.csv', NULL),
('NBA_API', 'failed', '2025-01-03 02:00:00', '2025-01-03 02:05:15', 0, 500, 'system', 'nba_daily_feed.json', 'API timeout after 30 seconds'),
('ESPN_Feed', 'completed', '2025-01-03 02:30:00', '2025-01-03 02:38:22', 890, 12, 'system', 'espn_stats.csv', NULL),
('Manual_Entry', 'completed', '2025-01-03 14:30:00', '2025-01-03 14:35:45', 25, 0, 'analyst1', 'injury_report.xlsx', NULL),
('NBA_API', 'completed', '2025-01-04 02:00:00', '2025-01-04 02:16:33', 1280, 3, 'system', 'nba_daily_feed.json', NULL),
('Video_Analysis', 'completed', '2025-01-04 04:00:00', '2025-01-04 04:45:12', 156, 2, 'system', 'game_footage_batch_1.mp4', NULL),
('Stats_API', 'completed', '2025-01-04 03:00:00', '2025-01-04 03:22:18', 1190, 15, 'system', 'advanced_stats.json', NULL),
('Referee_Data', 'completed', '2025-01-05 08:00:00', '2025-01-05 08:08:45', 89, 0, 'system', 'referee_assignments.json', NULL),
('NBA_API', 'completed', '2025-01-05 02:00:00', '2025-01-05 02:13:27', 1320, 1, 'system', 'nba_daily_feed.json', NULL),
('ESPN_Feed', 'completed', '2025-01-05 02:30:00', '2025-01-05 02:41:33', 945, 8, 'system', 'espn_stats.csv', NULL),
('Injury_Update', 'completed', '2025-01-05 12:00:00', '2025-01-05 12:02:15', 18, 0, 'team_doc', 'daily_injury_report.json', NULL),
('NBA_API', 'failed', '2025-01-06 02:00:00', '2025-01-06 02:08:42', 234, 456, 'system', 'nba_daily_feed.json', 'Partial data corruption detected'),
('Stats_API', 'completed', '2025-01-06 03:00:00', '2025-01-06 03:19:55', 1167, 22, 'system', 'advanced_stats.json', NULL),
('Trade_Data', 'completed', '2025-01-06 15:30:00', '2025-01-06 15:33:12', 8, 0, 'gm', 'trade_deadline_moves.csv', NULL),
('NBA_API', 'completed', '2025-01-07 02:00:00', '2025-01-07 02:18:44', 1355, 0, 'system', 'nba_daily_feed.json', NULL),
('ESPN_Feed', 'completed', '2025-01-07 02:30:00', '2025-01-07 02:39:17', 923, 11, 'system', 'espn_stats.csv', NULL),
('Draft_Prospects', 'completed', '2025-01-07 10:00:00', '2025-01-07 10:12:33', 234, 3, 'scout', 'college_prospects.xlsx', NULL),
('NBA_API', 'completed', '2025-01-08 02:00:00', '2025-01-08 02:15:22', 1298, 4, 'system', 'nba_daily_feed.json', NULL),
('Video_Analysis', 'failed', '2025-01-08 04:00:00', '2025-01-08 04:15:33', 12, 144, 'system', 'game_footage_batch_2.mp4', 'Video codec not supported'),
('Stats_API', 'completed', '2025-01-08 03:00:00', '2025-01-08 03:21:45', 1201, 18, 'system', 'advanced_stats.json', NULL),
('Salary_Data', 'completed', '2025-01-08 16:00:00', '2025-01-08 16:05:27', 467, 0, 'finance', 'salary_cap_update.csv', NULL),
('NBA_API', 'completed', '2025-01-09 02:00:00', '2025-01-09 02:14:18', 1332, 2, 'system', 'nba_daily_feed.json', NULL),
('ESPN_Feed', 'completed', '2025-01-09 02:30:00', '2025-01-09 02:43:55', 967, 6, 'system', 'espn_stats.csv', NULL),
('Agent_Data', 'completed', '2025-01-09 11:00:00', '2025-01-09 11:03:44', 78, 0, 'admin', 'agent_contact_updates.json', NULL),
('NBA_API', 'completed', '2025-01-10 02:00:00', '2025-01-10 02:16:55', 1289, 7, 'system', 'nba_daily_feed.json', NULL),
('Stats_API', 'completed', '2025-01-10 03:00:00', '2025-01-10 03:20:33', 1178, 25, 'system', 'advanced_stats.json', NULL),
('Venue_Data', 'completed', '2025-01-10 09:00:00', '2025-01-10 09:02:15', 30, 0, 'facilities', 'arena_capacity_updates.csv', NULL),
('NBA_API', 'failed', '2025-01-11 02:00:00', '2025-01-11 02:12:22', 455, 845, 'system', 'nba_daily_feed.json', 'Rate limit exceeded'),
('ESPN_Feed', 'completed', '2025-01-11 02:30:00', '2025-01-11 02:37:18', 912, 9, 'system', 'espn_stats.csv', NULL),
('Medical_Data', 'completed', '2025-01-11 13:00:00', '2025-01-11 13:08:45', 145, 2, 'medical', 'player_health_metrics.xlsx', NULL),
('NBA_API', 'completed', '2025-01-12 02:00:00', '2025-01-12 02:17:33', 1345, 1, 'system', 'nba_daily_feed.json', NULL),
('Stats_API', 'completed', '2025-01-12 03:00:00', '2025-01-12 03:19:44', 1198, 31, 'system', 'advanced_stats.json', NULL),
('Schedule_Update', 'completed', '2025-01-12 08:00:00', '2025-01-12 08:01:55', 82, 0, 'league', 'schedule_changes.json', NULL),
('NBA_API', 'completed', '2025-01-13 02:00:00', '2025-01-13 02:15:27', 1313, 5, 'system', 'nba_daily_feed.json', NULL),
('ESPN_Feed', 'completed', '2025-01-13 02:30:00', '2025-01-13 02:41:12', 934, 13, 'system', 'espn_stats.csv', NULL),
('Coaching_Data', 'completed', '2025-01-13 14:00:00', '2025-01-13 14:06:33', 67, 0, 'coach', 'play_call_analysis.csv', NULL),
('NBA_API', 'completed', '2025-01-14 02:00:00', '2025-01-14 02:16:18', 1298, 3, 'system', 'nba_daily_feed.json', NULL),
('Video_Analysis', 'completed', '2025-01-14 04:00:00', '2025-01-14 04:52:17', 189, 8, 'system', 'game_footage_batch_3.mp4', NULL),
('Stats_API', 'completed', '2025-01-14 03:00:00', '2025-01-14 03:22:55', 1205, 19, 'system', 'advanced_stats.json', NULL),
('Fan_Data', 'completed', '2025-01-14 10:00:00', '2025-01-14 10:15:44', 15678, 234, 'marketing', 'fan_engagement_metrics.csv', NULL),
('NBA_API', 'completed', '2025-01-15 02:00:00', '2025-01-15 02:14:39', 1327, 2, 'system', 'nba_daily_feed.json', NULL),
('ESPN_Feed', 'completed', '2025-01-15 02:30:00', '2025-01-15 02:38:45', 956, 7, 'system', 'espn_stats.csv', NULL),
('Broadcast_Data', 'completed', '2025-01-15 12:00:00', '2025-01-15 12:08:22', 234, 1, 'broadcast', 'tv_ratings.xlsx', NULL),
('NBA_API', 'completed', '2025-01-16 02:00:00', '2025-01-16 02:17:11', 1342, 4, 'system', 'nba_daily_feed.json', NULL),
('Stats_API', 'completed', '2025-01-16 03:00:00', '2025-01-16 03:21:33', 1189, 28, 'system', 'advanced_stats.json', NULL),
('Social_Media', 'completed', '2025-01-16 11:00:00', '2025-01-16 11:25:18', 4567, 89, 'social_team', 'social_mentions.json', NULL),
('NBA_API', 'failed', '2025-01-17 02:00:00', '2025-01-17 02:05:44', 0, 678, 'system', 'nba_daily_feed.json', 'Server maintenance window'),
('ESPN_Feed', 'completed', '2025-01-17 02:30:00', '2025-01-17 02:44:17', 923, 14, 'system', 'espn_stats.csv', NULL),
('Scouting_Report', 'completed', '2025-01-17 15:00:00', '2025-01-17 15:18:55', 123, 2, 'scout', 'prospect_evaluations.docx', NULL),
('NBA_API', 'completed', '2025-01-18 02:00:00', '2025-01-18 02:16:22', 1356, 1, 'system', 'nba_daily_feed.json', NULL),
('Stats_API', 'completed', '2025-01-18 03:00:00', '2025-01-18 03:20:44', 1212, 22, 'system', 'advanced_stats.json', NULL),
('Contract_Data', 'completed', '2025-01-18 16:00:00', '2025-01-18 16:04:33', 89, 0, 'legal', 'contract_extensions.pdf', NULL),
('NBA_API', 'completed', '2025-01-19 02:00:00', '2025-01-19 02:15:55', 1334, 6, 'system', 'nba_daily_feed.json', NULL),
('ESPN_Feed', 'completed', '2025-01-19 02:30:00', '2025-01-19 02:39:28', 941, 10, 'system', 'espn_stats.csv', NULL),
('Analytics_Batch', 'completed', '2025-01-19 05:00:00', '2025-01-19 05:45:17', 2345, 67, 'system', 'nightly_analytics.parquet', NULL),
('NBA_API', 'completed', '2025-01-20 02:00:00', '2025-01-20 02:17:44', 1318, 8, 'system', 'nba_daily_feed.json', NULL);

-- ErrorLogs (65 rows - system error tracking)
INSERT INTO ErrorLogs (error_type, severity, module, error_message, user_id, created_at, resolved_at, resolved_by, resolution_notes, stack_trace) VALUES
('DataQuality', 'warning', 'DataValidation', 'Found 3 players with shooting percentage > 1.0', 1, '2025-01-15 08:15:30', '2025-01-15 09:30:00', 'analyst1', 'Data corrected and validation rules updated', NULL),
('APITimeout', 'error', 'DataIngestion', 'NBA API request timeout after 30 seconds', 1, '2025-01-15 02:05:15', '2025-01-15 08:00:00', 'system', 'Retry mechanism triggered, successful on retry', 'APIConnector.timeout.exception'),
('DatabaseConnection', 'critical', 'SystemHealth', 'Lost connection to replica database', NULL, '2025-01-14 14:22:18', '2025-01-14 14:45:33', 'dba_team', 'Database failover completed', 'Connection.pool.exhausted'),
('DataIntegrity', 'error', 'DataValidation', 'Duplicate game entries detected for game_id 156', 1, '2025-01-13 10:15:45', '2025-01-13 11:30:22', 'data_admin', 'Duplicate records removed', NULL),
('MemoryLimit', 'warning', 'CacheLayer', 'Cache memory limit exceeded, clearing old entries', NULL, '2025-01-12 16:45:12', NULL, NULL, NULL, 'Memory.allocation.exceeded'),
('ValidationError', 'error', 'PlayerStats', 'Invalid minutes played value: 65 minutes in single game', 2, '2025-01-12 09:30:44', '2025-01-12 10:15:18', 'stats_validator', 'Corrected to 45 minutes based on game log', NULL),
('FileCorruption', 'critical', 'DataIngestion', 'ESPN feed file corrupted during transfer', NULL, '2025-01-11 02:33:27', '2025-01-11 03:15:45', 'file_admin', 'Restored from backup, re-processed data', 'File.checksum.mismatch'),
('AccessDenied', 'warning', 'UserAuth', 'User attempted access to restricted coaching data', 4, '2025-01-11 14:22:33', '2025-01-11 14:25:12', 'security_admin', 'User permissions reviewed and updated', NULL),
('RateLimitExceeded', 'error', 'ExternalAPI', 'ESPN API rate limit exceeded', NULL, '2025-01-10 11:45:22', '2025-01-10 12:00:00', 'api_manager', 'Implemented backoff strategy', 'RateLimit.quota.exceeded'),
('DataMissing', 'warning', 'GameStats', 'Missing player stats for player_id 245 in game_id 123', 3, '2025-01-10 08:12:17', '2025-01-10 09:45:33', 'stats_entry', 'Manual entry completed', NULL),
('ProcessingError', 'error', 'VideoAnalysis', 'Failed to process game footage - unsupported codec', NULL, '2025-01-09 04:15:33', '2025-01-09 10:30:18', 'video_tech', 'Codec updated, reprocessed successfully', 'Video.codec.unsupported'),
('LoginFailure', 'warning', 'UserAuth', 'Multiple failed login attempts for user: coach_smith', NULL, '2025-01-09 07:33:45', '2025-01-09 08:00:12', 'security_team', 'Account temporarily locked, user contacted', NULL),
('DataInconsistency', 'error', 'TeamRoster', 'Player assigned to multiple teams simultaneously', 2, '2025-01-08 15:45:27', '2025-01-08 16:30:44', 'roster_manager', 'Corrected team assignments', NULL),
('PerformanceDegradation', 'warning', 'DatabaseQuery', 'Query execution time exceeded 5 seconds', NULL, '2025-01-08 11:22:18', '2025-01-08 12:15:33', 'db_optimizer', 'Added index on frequently queried columns', 'Query.timeout.warning'),
('ConfigurationError', 'error', 'SystemSetup', 'Missing environment variable: NBA_API_KEY', NULL, '2025-01-07 09:15:44', '2025-01-07 09:20:12', 'devops_team', 'Environment variable added', NULL),
('DataValidation', 'warning', 'PlayerProfile', 'Inconsistent height format in player data', 1, '2025-01-07 13:30:22', '2025-01-07 14:15:45', 'data_cleaner', 'Standardized height format across all records', NULL),
('NetworkError', 'error', 'DataSync', 'Failed to sync with external statistics provider', NULL, '2025-01-06 23:45:18', '2025-01-07 00:30:33', 'network_admin', 'Network connectivity restored', 'Network.connection.failed'),
('SchedulingConflict', 'warning', 'GameSchedule', 'Overlapping game times detected', 3, '2025-01-06 16:22:44', '2025-01-06 17:00:15', 'scheduler', 'Game times adjusted to resolve conflict', NULL),
('StorageLimit', 'error', 'FileSystem', 'Video storage approaching 95% capacity', NULL, '2025-01-06 12:15:33', '2025-01-06 18:30:22', 'storage_admin', 'Archived old videos, expanded storage', 'Storage.capacity.warning'),
('AuthenticationTimeout', 'warning', 'UserSession', 'User session expired during data entry', 2, '2025-01-05 14:45:27', '2025-01-05 14:47:12', 'session_manager', 'Data recovered from temp storage', NULL),
('CalculationError', 'error', 'Analytics', 'Division by zero in efficiency calculation', NULL, '2025-01-05 10:30:18', '2025-01-05 11:15:44', 'analytics_dev', 'Added null check in calculation logic', 'Math.divisionByZero'),
('InputValidation', 'warning', 'FormSubmission', 'Invalid email format in user registration', NULL, '2025-01-04 16:33:55', '2025-01-04 16:35:22', 'form_validator', 'Email format validation strengthened', NULL),
('CacheFailure', 'error', 'PerformanceLayer', 'Redis cache cluster node failure', NULL, '2025-01-04 08:22:17', '2025-01-04 09:45:33', 'cache_admin', 'Failover to backup cache node completed', 'Cache.node.unreachable'),
('DataSynchronization', 'critical', 'ReplicationSystem', 'Master-slave replication lag exceeding 30 minutes', NULL, '2025-01-03 22:15:44', '2025-01-04 01:30:18', 'dba_team', 'Replication resynchronized', 'Replication.lag.critical'),
('ResourceExhaustion', 'error', 'SystemResources', 'CPU usage sustained above 90% for 10 minutes', NULL, '2025-01-03 15:45:22', '2025-01-03 16:30:44', 'sys_admin', 'Scaled up server resources', 'CPU.usage.critical'),
('BackupFailure', 'critical', 'DataProtection', 'Nightly backup failed - insufficient disk space', NULL, '2025-01-03 03:00:12', '2025-01-03 08:15:33', 'backup_admin', 'Cleared old backups, backup completed', 'Backup.disk.space.insufficient'),
('ParseError', 'error', 'DataProcessing', 'JSON parsing failed for player statistics file', NULL, '2025-01-02 11:22:45', '2025-01-02 12:45:18', 'data_processor', 'File format corrected and reprocessed', 'JSON.parse.malformed'),
('SecurityBreach', 'critical', 'Security', 'Attempted SQL injection in login form', NULL, '2025-01-02 09:15:33', '2025-01-02 09:30:12', 'security_team', 'IP blocked, form validation strengthened', 'Security.injection.attempt'),
('APIQuotaExceeded', 'warning', 'ExternalAPI', 'Daily API quota approaching limit', NULL, '2025-01-01 20:45:27', '2025-01-02 08:00:00', 'api_manager', 'Upgraded API plan to higher quota', NULL),
('DataCorruption', 'error', 'FileIntegrity', 'Checksum mismatch in game video file', NULL, '2025-01-01 16:30:44', '2025-01-01 18:15:22', 'file_validator', 'File restored from backup', 'File.integrity.checksum'),
('ConnectionPool', 'warning', 'DatabaseConnections', 'Database connection pool 80% utilized', NULL, '2025-01-01 14:22:18', '2025-01-01 15:00:33', 'db_admin', 'Increased connection pool size', NULL),
('FeatureFlag', 'info', 'SystemConfiguration', 'New analytics feature enabled for beta testing', 1, '2025-01-01 10:15:45', NULL, NULL, NULL, NULL),
('LogRotation', 'info', 'SystemMaintenance', 'Log files rotated and archived', NULL, '2025-01-01 02:00:12', NULL, NULL, NULL, NULL),
('SystemStartup', 'info', 'SystemHealth', 'BallWatch system initialized successfully', NULL, '2025-01-01 00:00:15', NULL, NULL, NULL, NULL),
('DataExport', 'info', 'ReportGeneration', 'Season statistics exported for analysis', 3, '2024-12-31 23:45:33', NULL, NULL, NULL, NULL),
('UserRegistration', 'info', 'UserManagement', 'New analyst user registered: data_analyst_5', 1, '2024-12-31 16:22:44', NULL, NULL, NULL, NULL),
('PasswordReset', 'info', 'UserAuth', 'Password reset requested by user_id 15', NULL, '2024-12-31 14:15:18', '2024-12-31 14:20:33', 'user_support', 'Password reset email sent', NULL),
('SystemUpdate', 'info', 'SystemMaintenance', 'Analytics engine updated to version 2.3.1', NULL, '2024-12-30 02:00:00', '2024-12-30 02:30:45', 'devops_team', 'Update completed successfully', NULL),
('DataCleanup', 'info', 'DataMaintenance', 'Removed expired session data', NULL, '2024-12-29 03:15:22', NULL, NULL, NULL, NULL),
('PerformanceAlert', 'warning', 'SystemMonitoring', 'Page load time exceeding 3 seconds', NULL, '2024-12-28 15:45:18', '2024-12-28 16:30:44', 'performance_team', 'Optimized database queries', NULL),
('SSLRenewal', 'info', 'Security', 'SSL certificate renewed successfully', NULL, '2024-12-27 08:00:12', NULL, NULL, NULL, NULL),
('MaintenanceWindow', 'info', 'SystemMaintenance', 'Scheduled maintenance completed', NULL, '2024-12-26 04:00:00', '2024-12-26 06:30:18', 'maintenance_team', 'All systems operational', NULL),
('BandwidthLimit', 'warning', 'NetworkMonitoring', 'Bandwidth usage approaching monthly limit', NULL, '2024-12-25 18:22:33', '2024-12-26 08:15:45', 'network_admin', 'Optimized video streaming quality', NULL),
('ConfigUpdate', 'info', 'SystemConfiguration', 'Updated API rate limiting configuration', NULL, '2024-12-24 12:30:44', NULL, NULL, NULL, NULL),
('DatabaseMigration', 'info', 'DataMaintenance', 'Migrated legacy player data to new schema', NULL, '2024-12-23 01:00:15', '2024-12-23 03:45:22', 'migration_team', 'Migration completed successfully', NULL),
('IntegrationTest', 'info', 'QualityAssurance', 'API integration tests passed', NULL, '2024-12-22 16:15:33', NULL, NULL, NULL, NULL),
('MonitoringAlert', 'warning', 'SystemHealth', 'Disk usage on analytics server above 85%', NULL, '2024-12-21 20:45:18', '2024-12-22 08:30:12', 'sys_admin', 'Cleaned up temporary files', NULL),
('LoadTesting', 'info', 'PerformanceTesting', 'System load test completed successfully', NULL, '2024-12-20 14:22:44', NULL, NULL, NULL, NULL),
('SecurityScan', 'info', 'Security', 'Monthly security scan completed - no issues found', NULL, '2024-12-19 10:15:27', NULL, NULL, NULL, NULL),
('FeatureDeployment', 'info', 'SystemDevelopment', 'New player comparison feature deployed', NULL, '2024-12-18 16:30:45', NULL, NULL, NULL, NULL),
('CacheWarmup', 'info', 'PerformanceOptimization', 'Cache preloaded with frequently accessed data', NULL, '2024-12-17 02:15:18', NULL, NULL, NULL, NULL),
('UserFeedback', 'info', 'CustomerSupport', 'Positive feedback received for new dashboard', NULL, '2024-12-16 11:45:33', NULL, NULL, NULL, NULL),
('APIVersioning', 'info', 'SystemDevelopment', 'Deprecated API v1.0, all clients migrated to v2.0', NULL, '2024-12-15 09:22:12', NULL, NULL, NULL, NULL),
('DataArchival', 'info', 'DataMaintenance', 'Archived 2019-2020 season data to cold storage', NULL, '2024-12-14 03:30:44', '2024-12-14 06:15:27', 'archive_team', 'Archival completed successfully', NULL),
('SystemMetrics', 'info', 'SystemMonitoring', 'Monthly system health report generated', NULL, '2024-12-13 23:45:18', NULL, NULL, NULL, NULL),
('DatabaseOptimization', 'info', 'PerformanceImprovement', 'Optimized queries for player statistics retrieval', NULL, '2024-12-12 15:22:33', NULL, NULL, NULL, NULL),
('ComplianceCheck', 'info', 'DataGovernance', 'GDPR compliance audit completed successfully', NULL, '2024-12-11 14:15:45', NULL, NULL, NULL, NULL),
('ServiceUpgrade', 'info', 'SystemMaintenance', 'Analytics service upgraded to support real-time data', NULL, '2024-12-10 02:30:12', '2024-12-10 04:45:33', 'upgrade_team', 'Upgrade completed with zero downtime', NULL),
('AlertThreshold', 'warning', 'SystemMonitoring', 'Memory usage consistently above 80%', NULL, '2024-12-09 16:45:27', '2024-12-10 08:30:18', 'sys_admin', 'Added more RAM to servers', NULL),
('DataValidationUpdate', 'info', 'SystemImprovement', 'Enhanced data validation rules for player statistics', NULL, '2024-12-08 11:15:44', NULL, NULL, NULL, NULL),
('BackupVerification', 'info', 'DataProtection', 'Backup integrity verification completed successfully', NULL, '2024-12-07 04:00:22', NULL, NULL, NULL, NULL),
('UserTraining', 'info', 'UserSupport', 'Training session completed for new analytics features', NULL, '2024-12-06 13:30:33', NULL, NULL, NULL, NULL),
('ThirdPartyIntegration', 'info', 'SystemIntegration', 'Successfully integrated with new video analysis provider', NULL, '2024-12-05 10:45:18', NULL, NULL, NULL, NULL),
('SeasonRollover', 'info', 'DataManagement', 'Prepared system for 2024-25 season data', NULL, '2024-12-04 01:15:27', '2024-12-04 03:30:44', 'data_team', 'Season rollover completed successfully', NULL),
('PerformanceBenchmark', 'info', 'QualityAssurance', 'System performance benchmarks established', NULL, '2024-12-03 17:22:15', NULL, NULL, NULL, NULL),
('RedundancyTest', 'info', 'SystemReliability', 'Failover systems tested successfully', NULL, '2024-12-02 08:45:33', NULL, NULL, NULL, NULL);

-- DataErrors (52 rows - data quality issues)
INSERT INTO DataErrors (error_type, table_name, record_id, field_name, invalid_value, expected_format, detected_at, resolved_at, auto_fixed) VALUES
('invalid', 'PlayerGameStats', '123', 'shooting_percentage', '1.25', 'Decimal between 0 and 1', '2025-01-15 08:15:30', '2025-01-15 09:30:00', TRUE),
('duplicate', 'Game', '456', 'game_id', '456', 'Unique identifier', '2025-01-13 10:15:45', '2025-01-13 11:30:22', FALSE),
('missing', 'Players', '789', 'position', NULL, 'Required enum value', '2025-01-12 14:22:18', '2025-01-12 15:45:33', FALSE),
('invalid', 'PlayerGameStats', '234', 'minutes_played', '65', 'Integer 0-48', '2025-01-12 09:30:44', '2025-01-12 10:15:18', TRUE),
('invalid', 'Players', '567', 'height', '6-15', 'Format: 6-10', '2025-01-11 16:45:27', '2025-01-11 17:30:12', TRUE),
('duplicate', 'TeamsPlayers', '890', 'player_id,team_id', '15,3', 'Unique combination', '2025-01-10 11:22:33', '2025-01-10 12:45:18', FALSE),
('missing', 'Game', '345', 'home_team_id', NULL, 'Required foreign key', '2025-01-09 13:15:44', '2025-01-09 14:30:27', FALSE),
('invalid', 'PlayerGameStats', '678', 'three_point_percentage', '-0.15', 'Non-negative decimal', '2025-01-08 10:45:18', '2025-01-08 11:30:33', TRUE),
('invalid', 'Teams', '123', 'founded_year', '2025', 'Year <= current year', '2025-01-07 15:22:44', '2025-01-07 16:15:27', TRUE),
('missing', 'PlayerGameStats', '456', 'points', NULL, 'Required integer >= 0', '2025-01-06 09:30:15', '2025-01-06 10:45:22', FALSE),
('duplicate', 'Users', '789', 'email', 'coach@team.com', 'Unique email address', '2025-01-05 14:15:33', '2025-01-05 15:30:18', FALSE),
('invalid', 'Players', '234', 'age', '55', 'Reasonable age range 18-45', '2025-01-04 12:22:27', '2025-01-04 13:45:44', TRUE),
('invalid', 'Game', '567', 'home_score', '-5', 'Non-negative integer', '2025-01-03 16:30:12', '2025-01-03 17:15:33', TRUE),
('missing', 'DraftEvaluations', '890', 'overall_rating', NULL, 'Required rating 0-100', '2025-01-02 11:45:18', '2025-01-02 12:30:44', FALSE),
('invalid', 'PlayerMatchup', '345', 'shooting_percentage', '1.8', 'Percentage 0.0-1.0', '2025-01-01 14:22:33', '2025-01-01 15:15:27', TRUE),
('duplicate', 'Agent', '678', 'email', 'agent@agency.com', 'Unique email', '2024-12-31 10:30:15', '2024-12-31 11:45:22', FALSE),
('invalid', 'LineupConfiguration', '123', 'quarter', '5', 'Quarter 1-4', '2024-12-30 13:15:44', '2024-12-30 14:30:18', TRUE),
('missing', 'GamePlans', '456', 'team_id', NULL, 'Required foreign key', '2024-12-29 09:22:27', '2024-12-29 10:45:33', FALSE),
('invalid', 'PlayerGameStats', '789', 'rebounds', '-2', 'Non-negative integer', '2024-12-28 15:45:12', '2024-12-28 16:30:44', TRUE),
('invalid', 'Teams', '234', 'conference', 'Central', 'Must be Eastern or Western', '2024-12-27 11:15:33', '2024-12-27 12:30:18', TRUE),
('duplicate', 'Game', '567', 'game_date,home_team_id', '2024-12-26,5', 'Unique game per date/team', '2024-12-26 16:22:44', '2024-12-26 17:45:27', FALSE),
('missing', 'Players', '890', 'first_name', NULL, 'Required field', '2024-12-25 14:30:15', '2024-12-25 15:15:33', FALSE),
('invalid', 'PlayerGameStats', '345', 'assists', '25', 'Reasonable assists 0-20', '2024-12-24 12:45:22', '2024-12-24 13:30:44', TRUE),
('invalid', 'Agent', '678', 'phone', '555-ABCD', 'Valid phone format', '2024-12-23 10:15:27', '2024-12-23 11:30:18', TRUE),
('duplicate', 'TeamsPlayers', '123', 'player_id,team_id,joined_date', '25,8,2024-01-01', 'Unique assignment', '2024-12-22 13:22:33', '2024-12-22 14:45:15', FALSE),
('invalid', 'Game', '456', 'attendance', '50000', 'Cannot exceed venue capacity', '2024-12-21 15:45:18', '2024-12-21 16:30:27', TRUE),
('missing', 'PlayerMatchup', '789', 'offensive_player_id', NULL, 'Required foreign key', '2024-12-20 11:30:44', '2024-12-20 12:15:33', FALSE),
('invalid', 'DraftEvaluations', '234', 'potential_rating', '105', 'Rating must be 0-100', '2024-12-19 14:15:22', '2024-12-19 15:30:18', TRUE),
('invalid', 'Players', '567', 'weight', '350', 'Reasonable weight 150-350', '2024-12-18 09:45:33', '2024-12-18 10:30:27', TRUE),
('duplicate', 'GamePlans', '890', 'team_id,game_id', '12,78', 'One plan per team per game', '2024-12-17 12:22:15', '2024-12-17 13:45:44', FALSE),
('invalid', 'PlayerGameStats', '345', 'steals', '-1', 'Non-negative integer', '2024-12-16 16:30:18', '2024-12-16 17:15:27', TRUE),
('missing', 'Teams', '678', 'name', NULL, 'Required team name', '2024-12-15 10:45:22', '2024-12-15 11:30:33', FALSE),
('invalid', 'Game', '123', 'game_time', '25:30:00', 'Valid time format HH:MM:SS', '2024-12-14 13:15:44', '2024-12-14 14:30:18', TRUE),
('invalid', 'PlayerGameStats', '456', 'blocks', '15', 'Reasonable blocks 0-10', '2024-12-13 11:22:33', '2024-12-13 12:45:27', TRUE),
('duplicate', 'Users', '789', 'username', 'admin123', 'Unique username', '2024-12-12 14:45:15', '2024-12-12 15:30:44', FALSE),
('invalid', 'Players', '234', 'draft_year', '1950', 'Valid NBA draft year', '2024-12-11 09:30:22', '2024-12-11 10:15:18', TRUE),
('missing', 'LineupConfiguration', '567', 'team_id', NULL, 'Required foreign key', '2024-12-10 12:15:33', '2024-12-10 13:30:27', FALSE),
('invalid', 'PlayerMatchup', '890', 'possessions', '0', 'Must be positive integer', '2024-12-09 15:45:44', '2024-12-09 16:30:15', TRUE),
('invalid', 'Game', '345', 'season', '2025-26', 'Format: YYYY-YY', '2024-12-08 10:22:27', '2024-12-08 11:45:33', TRUE),
('duplicate', 'Agent', '678', 'first_name,last_name', 'John,Smith', 'Likely duplicate agent', '2024-12-07 13:30:18', '2024-12-07 14:15:44', FALSE),
('invalid', 'PlayerGameStats', '123', 'free_throw_percentage', '1.5', 'Percentage 0.0-1.0', '2024-12-06 16:15:22', '2024-12-06 17:30:33', TRUE),
('missing', 'DraftEvaluations', '456', 'player_id', NULL, 'Required foreign key', '2024-12-05 11:45:27', '2024-12-05 12:30:18', FALSE),
('invalid', 'Teams', '789', 'championships', '-1', 'Non-negative integer', '2024-12-04 14:22:15', '2024-12-04 15:45:44', TRUE),
('invalid', 'Players', '234', 'current_salary', '-5000000', 'Non-negative salary', '2024-12-03 12:30:33', '2024-12-03 13:15:27', TRUE),
('duplicate', 'Game', '567', 'home_team_id,away_team_id,game_date', '5,8,2024-01-15', 'Teams cannot play twice same day', '2024-12-02 15:45:18', '2024-12-02 16:30:44', FALSE),
('invalid', 'PlayerGameStats', '890', 'plus_minus', '75', 'Reasonable plus_minus range -50 to +50', '2024-12-01 09:22:44', '2024-12-01 10:45:15', TRUE),
('missing', 'TeamsPlayers', '345', 'joined_date', NULL, 'Required join date', '2024-11-30 11:15:33', '2024-11-30 12:30:27', FALSE),
('invalid', 'Agent', '678', 'agency_name', '', 'Agency name cannot be empty', '2024-11-29 13:45:22', '2024-11-29 14:30:18', TRUE),
('invalid', 'Game', '123', 'venue', '', 'Venue cannot be empty', '2024-11-28 16:30:44', '2024-11-28 17:15:33', TRUE),
('duplicate', 'PlayerLineups', '456', 'player_id,lineup_id', '25,15', 'Player cannot be in same lineup twice', '2024-11-27 10:22:15', '2024-11-27 11:45:27', FALSE),
('invalid', 'LineupConfiguration', '789', 'plus_minus', '125', 'Unrealistic plus_minus value', '2024-11-26 12:45:33', '2024-11-26 13:30:18', TRUE),
('missing', 'GamePlans', '234', 'plan_name', NULL, 'Required plan name', '2024-11-25 14:15:44', '2024-11-25 15:30:22', FALSE),
('invalid', 'PlayerMatchup', '567', 'points_scored', '95', 'Unrealistic points in matchup', '2024-11-24 11:30:27', '2024-11-24 12:15:18', TRUE);

-- CleanupSchedule (18 rows - automated cleanup tasks)
INSERT INTO CleanupSchedule (cleanup_type, frequency, next_run, last_run, retention_days, is_active, created_by, created_at) VALUES
('ErrorLogs', 'weekly', '2025-01-26 02:00:00', '2025-01-19 02:00:00', 90, TRUE, 'system_admin', '2024-01-01 10:00:00'),
('DataLoads', 'monthly', '2025-02-01 03:00:00', '2025-01-01 03:00:00', 180, TRUE, 'system_admin', '2024-01-01 10:15:00'),
('TempFiles', 'daily', '2025-01-25 01:00:00', '2025-01-24 01:00:00', 1, TRUE, 'file_manager', '2024-01-01 10:30:00'),
('UserSessions', 'daily', '2025-01-25 04:00:00', '2025-01-24 04:00:00', 30, TRUE, 'security_admin', '2024-01-01 11:00:00'),
('SystemHealth', 'weekly', '2025-01-26 05:00:00', '2025-01-19 05:00:00', 30, TRUE, 'monitoring_admin', '2024-01-01 11:30:00'),
('CacheEntries', 'daily', '2025-01-25 06:00:00', '2025-01-24 06:00:00', 7, TRUE, 'performance_admin', '2024-01-01 12:00:00'),
('ValidationReports', 'monthly', '2025-02-01 07:00:00', '2025-01-01 07:00:00', 365, TRUE, 'data_admin', '2024-01-01 12:30:00'),
('BackupFiles', 'weekly', '2025-01-26 08:00:00', '2025-01-19 08:00:00', 30, TRUE, 'backup_admin', '2024-01-01 13:00:00'),
('ArchivedGames', 'monthly', '2025-02-01 02:00:00', '2025-01-01 02:00:00', 1095, TRUE, 'archive_admin', '2024-01-01 13:30:00'),
('ExpiredTokens', 'daily', '2025-01-25 03:00:00', '2025-01-24 03:00:00', 1, TRUE, 'auth_admin', '2024-01-01 14:00:00'),
('ProcessingLogs', 'weekly', '2025-01-26 04:00:00', '2025-01-19 04:00:00', 60, TRUE, 'process_admin', '2024-01-01 14:30:00'),
('AnalyticsTemp', 'daily', '2025-01-25 05:00:00', '2025-01-24 05:00:00', 3, TRUE, 'analytics_admin', '2024-01-01 15:00:00'),
('VideoCache', 'weekly', '2025-01-26 06:00:00', '2025-01-19 06:00:00', 14, TRUE, 'video_admin', '2024-01-01 15:30:00'),
('NotificationQueue', 'daily', '2025-01-25 07:00:00', '2025-01-24 07:00:00', 7, TRUE, 'notification_admin', '2024-01-01 16:00:00'),
('SearchIndexes', 'weekly', '2025-01-26 09:00:00', '2025-01-19 09:00:00', 90, TRUE, 'search_admin', '2024-01-01 16:30:00'),
('AuditLogs', 'monthly', '2025-02-01 10:00:00', '2025-01-01 10:00:00', 2555, TRUE, 'audit_admin', '2024-01-01 17:00:00'),
('ReportCache', 'weekly', '2025-01-26 11:00:00', '2025-01-19 11:00:00', 30, TRUE, 'report_admin', '2024-01-01 17:30:00'),
('MetricsData', 'monthly', '2025-02-01 12:00:00', '2025-01-01 12:00:00', 365, TRUE, 'metrics_admin', '2024-01-01 18:00:00');

-- CleanupHistory (45 rows - cleanup execution history)
INSERT INTO CleanupHistory (schedule_id, cleanup_type, started_at, completed_at, records_deleted, status, error_message) VALUES
(1, 'ErrorLogs', '2025-01-19 02:00:00', '2025-01-19 02:15:33', 145, 'completed', NULL),
(2, 'DataLoads', '2025-01-01 03:00:00', '2025-01-01 03:22:18', 234, 'completed', NULL),
(3, 'TempFiles', '2025-01-24 01:00:00', '2025-01-24 01:05:27', 67, 'completed', NULL),
(4, 'UserSessions', '2025-01-24 04:00:00', '2025-01-24 04:02:15', 89, 'completed', NULL),
(5, 'SystemHealth', '2025-01-19 05:00:00', '2025-01-19 05:12:44', 456, 'completed', NULL),
(6, 'CacheEntries', '2025-01-24 06:00:00', '2025-01-24 06:03:33', 1234, 'completed', NULL),
(7, 'ValidationReports', '2025-01-01 07:00:00', '2025-01-01 07:08:15', 23, 'completed', NULL),
(8, 'BackupFiles', '2025-01-19 08:00:00', '2025-01-19 08:18:27', 12, 'completed', NULL),
(9, 'ArchivedGames', '2025-01-01 02:00:00', '2025-01-01 02:45:33', 567, 'completed', NULL),
(10, 'ExpiredTokens', '2025-01-24 03:00:00', '2025-01-24 03:01:15', 78, 'completed', NULL),
(11, 'ProcessingLogs', '2025-01-19 04:00:00', '2025-01-19 04:09:44', 189, 'completed', NULL),
(12, 'AnalyticsTemp', '2025-01-24 05:00:00', '2025-01-24 05:07:22', 345, 'completed', NULL),
(13, 'VideoCache', '2025-01-19 06:00:00', '2025-01-19 06:25:18', 23, 'completed', NULL),
(14, 'NotificationQueue', '2025-01-24 07:00:00', '2025-01-24 07:02:33', 156, 'completed', NULL),
(15, 'SearchIndexes', '2025-01-19 09:00:00', '2025-01-19 09:15:45', 789, 'completed', NULL),
(1, 'ErrorLogs', '2025-01-12 02:00:00', '2025-01-12 02:18:27', 123, 'completed', NULL),
(3, 'TempFiles', '2025-01-23 01:00:00', '2025-01-23 01:04:15', 45, 'completed', NULL),
(4, 'UserSessions', '2025-01-23 04:00:00', '2025-01-23 04:01:33', 67, 'completed', NULL),
(6, 'CacheEntries', '2025-01-23 06:00:00', '2025-01-23 06:02:44', 892, 'completed', NULL),
(10, 'ExpiredTokens', '2025-01-23 03:00:00', '2025-01-23 03:00:55', 34, 'completed', NULL),
(12, 'AnalyticsTemp', '2025-01-23 05:00:00', '2025-01-23 05:06:18', 234, 'completed', NULL),
(14, 'NotificationQueue', '2025-01-23 07:00:00', '2025-01-23 07:01:27', 78, 'completed', NULL),
(3, 'TempFiles', '2025-01-22 01:00:00', '2025-01-22 01:03:33', 56, 'completed', NULL),
(4, 'UserSessions', '2025-01-22 04:00:00', '2025-01-22 04:02:15', 89, 'completed', NULL),
(6, 'CacheEntries', '2025-01-22 06:00:00', '2025-01-22 06:04:22', 1456, 'completed', NULL),
(10, 'ExpiredTokens', '2025-01-22 03:00:00', '2025-01-22 03:01:44', 45, 'completed', NULL),
(12, 'AnalyticsTemp', '2025-01-22 05:00:00', '2025-01-22 05:08:15', 289, 'completed', NULL),
(14, 'NotificationQueue', '2025-01-22 07:00:00', '2025-01-22 07:02:33', 123, 'completed', NULL),
(5, 'SystemHealth', '2025-01-12 05:00:00', '2025-01-12 05:11:27', 378, 'completed', NULL),
(8, 'BackupFiles', '2025-01-12 08:00:00', '2025-01-12 08:16:44', 8, 'completed', NULL),
(11, 'ProcessingLogs', '2025-01-12 04:00:00', '2025-01-12 04:07:33', 167, 'completed', NULL),
(13, 'VideoCache', '2025-01-12 06:00:00', '2025-01-12 06:22:18', 19, 'completed', NULL),
(15, 'SearchIndexes', '2025-01-12 09:00:00', '2025-01-12 09:13:55', 634, 'completed', NULL),
(1, 'ErrorLogs', '2025-01-05 02:00:00', '2025-01-05 02:16:22', 134, 'completed', NULL),
(5, 'SystemHealth', '2025-01-05 05:00:00', '2025-01-05 05:10:44', 401, 'completed', NULL),
(8, 'BackupFiles', '2025-01-05 08:00:00', '2025-01-05 08:19:33', 11, 'completed', NULL),
(11, 'ProcessingLogs', '2025-01-05 04:00:00', '2025-01-05 04:08:15', 178, 'completed', NULL),
(13, 'VideoCache', '2025-01-05 06:00:00', '2025-01-05 06:24:27', 21, 'completed', NULL),
(15, 'SearchIndexes', '2025-01-05 09:00:00', '2025-01-05 09:14:18', 567, 'completed', NULL),
(6, 'CacheEntries', '2025-01-21 06:00:00', '2025-01-21 06:05:15', 1123, 'failed', 'Unable to connect to cache server'),
(12, 'AnalyticsTemp', '2025-01-20 05:00:00', '2025-01-20 05:09:33', 0, 'failed', 'Disk space insufficient'),
(3, 'TempFiles', '2025-01-19 01:00:00', '2025-01-19 01:02:44', 23, 'completed', NULL),
(14, 'NotificationQueue', '2025-01-18 07:00:00', '2025-01-18 07:03:27', 89, 'completed', NULL),
(10, 'ExpiredTokens', '2025-01-17 03:00:00', '2025-01-17 03:01:15', 67, 'completed', NULL),
(4, 'UserSessions', '2025-01-16 04:00:00', '2025-01-16 04:01:55', 112, 'completed', NULL);

-- ValidationReports (42 rows - data quality reports)
INSERT INTO ValidationReports (validation_type, table_name, status, total_records, valid_records, invalid_records, 
                             validation_rules, error_details, run_date, run_by) VALUES
('DataIntegrity', 'Players', 'passed', 38, 38, 0, '{"required_fields": ["first_name", "last_name"], "valid_positions": ["PG","SG","SF","PF","C","Guard","Forward","Center"]}', NULL, '2025-01-24 08:00:00', 'data_validator'),
('DataIntegrity', 'Teams', 'passed', 30, 30, 0, '{"required_fields": ["name", "conference"], "valid_conferences": ["Eastern", "Western"]}', NULL, '2025-01-24 08:15:00', 'data_validator'),
('DataIntegrity', 'Game', 'warning', 42, 40, 2, '{"score_rules": "home_score and away_score >= 0", "date_rules": "game_date not in future"}', 'Found 2 games with negative scores', '2025-01-24 08:30:00', 'data_validator'),
('DataIntegrity', 'PlayerGameStats', 'failed', 72, 68, 4, '{"percentage_rules": "all percentages between 0 and 1", "minutes_rules": "minutes_played <= 48"}', 'Found 4 records with invalid shooting percentages or minutes', '2025-01-24 08:45:00', 'data_validator'),
('ReferentialIntegrity', 'TeamsPlayers', 'passed', 135, 135, 0, '{"foreign_keys": ["player_id", "team_id"], "date_consistency": "left_date >= joined_date"}', NULL, '2025-01-24 09:00:00', 'data_validator'),
('DataIntegrity', 'Users', 'passed', 35, 35, 0, '{"email_format": "valid email address", "role_values": ["admin","coach","gm","analyst","fan"]}', NULL, '2025-01-24 09:15:00', 'data_validator'),
('ReferentialIntegrity', 'PlayerGameStats', 'warning', 72, 70, 2, '{"foreign_keys": ["player_id", "game_id"]}', 'Found 2 orphaned stats records', '2025-01-24 09:30:00', 'data_validator'),
('DataIntegrity', 'Agent', 'passed', 32, 32, 0, '{"email_format": "valid email address", "phone_format": "valid phone number"}', NULL, '2025-01-24 09:45:00', 'data_validator'),
('BusinessLogic', 'DraftEvaluations', 'passed', 58, 58, 0, '{"rating_range": "all ratings between 0 and 100", "required_fields": ["player_id", "overall_rating"]}', NULL, '2025-01-24 10:00:00', 'business_validator'),
('DataIntegrity', 'GamePlans', 'passed', 52, 52, 0, '{"required_fields": ["team_id", "plan_name"], "status_values": ["draft","active","archived"]}', NULL, '2025-01-24 10:15:00', 'data_validator'),
('DataIntegrity', 'PlayerMatchup', 'warning', 55, 53, 2, '{"percentage_rules": "shooting_percentage between 0 and 1", "possessions_rule": "possessions > 0"}', 'Found 2 matchups with invalid shooting percentages', '2025-01-23 08:00:00', 'data_validator'),
('BusinessLogic', 'LineupConfiguration', 'passed', 35, 35, 0, '{"quarter_range": "quarter between 1 and 4", "time_format": "valid time format"}', NULL, '2025-01-23 08:15:00', 'business_validator'),
('ReferentialIntegrity', 'PlayerLineups', 'passed', 0, 0, 0, '{"foreign_keys": ["player_id", "lineup_id"]}', 'Table is empty - no validation needed', '2025-01-23 08:30:00', 'data_validator'),
('DataIntegrity', 'SystemHealth', 'passed', 35, 35, 0, '{"percentage_rules": "error_rate_pct >= 0", "time_rules": "avg_response_time > 0"}', NULL, '2025-01-23 08:45:00', 'system_validator'),
('DataIntegrity', 'ErrorLogs', 'passed', 65, 65, 0, '{"severity_values": ["info","warning","error","critical"], "timestamp_rules": "created_at <= now()"}', NULL, '2025-01-23 09:00:00', 'system_validator'),
('DataIntegrity', 'DataLoads', 'warning', 58, 56, 2, '{"status_values": ["pending","running","completed","failed"], "record_counts": "records_processed >= 0"}', 'Found 2 loads with inconsistent record counts', '2025-01-23 09:15:00', 'system_validator'),
('DataIntegrity', 'DataErrors', 'passed', 52, 52, 0, '{"error_types": ["duplicate","missing","invalid"], "timestamp_rules": "detected_at <= now()"}', NULL, '2025-01-23 09:30:00', 'data_validator'),
('BusinessLogic', 'CleanupSchedule', 'passed', 18, 18, 0, '{"frequency_values": ["daily","weekly","monthly"], "retention_rules": "retention_days > 0"}', NULL, '2025-01-23 09:45:00', 'system_validator'),
('DataIntegrity', 'CleanupHistory', 'passed', 45, 45, 0, '{"status_values": ["started","completed","failed"], "time_consistency": "completed_at >= started_at"}', NULL, '2025-01-23 10:00:00', 'system_validator'),
('DataIntegrity', 'KeyMatchups', 'passed', 25, 25, 0, '{"required_fields": ["matchup_text"], "text_length": "matchup_text length > 10"}', NULL, '2025-01-22 08:00:00', 'data_validator'),
('BusinessLogic', 'Players', 'warning', 38, 36, 2, '{"age_range": "age between 18 and 45", "salary_rules": "current_salary >= 0", "experience_rules": "years_exp >= 0"}', 'Found 2 players with questionable age or salary data', '2025-01-22 08:15:00', 'business_validator'),
('BusinessLogic', 'Teams', 'passed', 30, 30, 0, '{"championship_rule": "championships >= 0", "founded_year": "founded_year <= current_year"}', NULL, '2025-01-22 08:30:00', 'business_validator'),
('DataConsistency', 'Game', 'warning', 42, 40, 2, '{"team_consistency": "home_team_id != away_team_id", "score_consistency": "completed games have scores"}', 'Found 2 games with missing scores for completed status', '2025-01-22 08:45:00', 'consistency_validator'),
('DataConsistency', 'PlayerGameStats', 'failed', 72, 65, 7, '{"stat_consistency": "points + rebounds + assists reasonable", "percentage_consistency": "shooting percentages consistent"}', 'Found 7 stat records with impossible or inconsistent values', '2025-01-22 09:00:00', 'consistency_validator'),
('BusinessLogic', 'TeamsPlayers', 'warning', 135, 130, 5, '{"date_logic": "left_date >= joined_date", "jersey_rules": "jersey_num between 0 and 99"}', 'Found 5 assignments with invalid jersey numbers or date inconsistencies', '2025-01-21 08:00:00', 'business_validator'),
('DataIntegrity', 'DraftEvaluations', 'passed', 58, 58, 0, '{"rating_consistency": "overall_rating correlates with sub-ratings", "text_fields": "strengths and weaknesses not empty"}', NULL, '2025-01-21 08:15:00', 'evaluation_validator'),
('BusinessLogic', 'GamePlans', 'warning', 52, 50, 2, '{"team_game_logic": "team_id and opponent_id different", "status_logic": "archived plans have completion dates"}', 'Found 2 game plans with logical inconsistencies', '2025-01-21 08:30:00', 'business_validator'),
('DataConsistency', 'PlayerMatchup', 'passed', 55, 55, 0, '{"player_consistency": "offensive and defensive players different", "game_consistency": "players actually played in referenced game"}', NULL, '2025-01-21 08:45:00', 'consistency_validator'),
('DataIntegrity', 'LineupConfiguration', 'passed', 35, 35, 0, '{"time_logic": "time_on > time_off", "rating_rules": "offensive and defensive ratings > 0"}', NULL, '2025-01-21 09:00:00', 'lineup_validator'),
('SystemIntegrity', 'SystemHealth', 'warning', 35, 33, 2, '{"service_availability": "critical services responding", "threshold_rules": "error rates within acceptable limits"}', 'Found 2 services with elevated error rates', '2025-01-20 08:00:00', 'system_monitor'),
('DataIntegrity', 'ErrorLogs', 'passed', 65, 65, 0, '{"severity_escalation": "critical errors properly escalated", "resolution_tracking": "resolved errors have resolution data"}', NULL, '2025-01-20 08:15:00', 'error_validator'),
('ProcessIntegrity', 'DataLoads', 'failed', 58, 52, 6, '{"load_consistency": "successful loads have processed records", "failure_analysis": "failed loads have error messages"}', 'Found 6 data loads with inconsistent status or missing error details', '2025-01-20 08:30:00', 'process_validator'),
('DataIntegrity', 'DataErrors', 'passed', 52, 52, 0, '{"error_resolution": "resolved errors have resolution dates", "error_classification": "errors properly categorized"}', NULL, '2025-01-20 08:45:00', 'error_validator'),
('SystemIntegrity', 'CleanupSchedule', 'passed', 18, 18, 0, '{"schedule_logic": "next_run after last_run", "retention_logic": "retention_days appropriate for cleanup_type"}', NULL, '2025-01-19 08:00:00', 'cleanup_validator'),
('ProcessIntegrity', 'CleanupHistory', 'warning', 45, 43, 2, '{"cleanup_effectiveness": "completed cleanups deleted records", "failure_analysis": "failed cleanups have error messages"}', 'Found 2 cleanup records with missing failure details', '2025-01-19 08:15:00', 'cleanup_validator'),
('DataIntegrity', 'KeyMatchups', 'passed', 25, 25, 0, '{"text_quality": "matchup descriptions meaningful", "uniqueness": "no duplicate matchup descriptions"}', NULL, '2025-01-18 08:00:00', 'matchup_validator'),
('OverallSystemHealth', 'ALL_TABLES', 'warning', 1205, 1150, 55, '{"system_wide": "comprehensive validation across all tables"}', 'Found 55 total validation issues across the system', '2025-01-24 10:30:00', 'system_wide_validator'),
('MonthlyAudit', 'ALL_TABLES', 'passed', 1205, 1188, 17, '{"monthly_audit": "comprehensive monthly data quality check"}', 'Monthly audit completed with minor issues', '2025-01-01 00:00:00', 'audit_system'),
('WeeklyCheck', 'PlayerGameStats', 'warning', 72, 69, 3, '{"weekly_stats": "player statistics consistency check"}', 'Found 3 statistical anomalies requiring review', '2025-01-20 00:00:00', 'weekly_validator'),
('DailyValidation', 'Game', 'passed', 42, 42, 0, '{"daily_games": "game data validation for current day"}', NULL, '2025-01-24 23:59:00', 'daily_validator'),
('QuarterlyReport', 'Teams', 'passed', 30, 30, 0, '{"quarterly_team": "team data comprehensive review"}', NULL, '2025-01-01 12:00:00', 'quarterly_validator'),
('SeasonValidation', 'Players', 'warning', 38, 36, 2, '{"season_player": "player data validation for current season"}', 'Found 2 players with outdated contract information', '2025-01-15 00:00:00', 'season_validator')

-- PlayerLineups (130 rows - players assigned to specific lineup configurations)
INSERT INTO PlayerLineups (player_id, lineup_id, position_in_lineup) VALUES
-- Nets Lineups (lineup_id 1-4)
-- Starting Lineup - Nets Q1
(1, 1, 'Small Forward'),    -- KD
(9, 1, 'Point Guard'),      -- Kyrie  
(15, 1, 'Power Forward'),   -- Ben Simmons
(19, 1, 'Shooting Guard'),  -- Herro (fictional assignment)
(28, 1, 'Center'),          -- Rob Williams (fictional)

-- Nets Q2 Bench Unit
(33, 2, 'Point Guard'),     -- Harper
(20, 2, 'Shooting Guard'),  -- Mikal Bridges (fictional)
(21, 2, 'Small Forward'),   -- OG Anunoby (fictional)
(24, 2, 'Power Forward'),   -- Barnes (fictional)
(36, 2, 'Center'),          -- Traore

-- Nets Q3 Closing Lineup
(1, 3, 'Small Forward'),    -- KD
(9, 3, 'Point Guard'),      -- Kyrie
(20, 3, 'Shooting Guard'),  -- Mikal
(21, 3, 'Power Forward'),   -- OG
(15, 3, 'Center'),          -- Simmons at center

-- Nets Q4 Small Ball
(1, 4, 'Power Forward'),    -- KD at 4
(9, 4, 'Point Guard'),      -- Kyrie
(33, 4, 'Shooting Guard'),  -- Harper
(20, 4, 'Small Forward'),   -- Mikal
(21, 4, 'Center'),          -- OG at center

-- Warriors Lineups (lineup_id 5-8)
-- Warriors Death Lineup Q1
(3, 5, 'Point Guard'),      -- Curry
(32, 5, 'Shooting Guard'),  -- Flagg
(25, 5, 'Small Forward'),   -- Franz (fictional)
(31, 5, 'Power Forward'),   -- Tucker (fictional)
(23, 5, 'Center'),          -- Sengun (fictional)

-- Warriors Bench Q2
(37, 6, 'Point Guard'),     -- Hugo
(22, 6, 'Shooting Guard'),  -- Green (fictional)
(38, 6, 'Small Forward'),   -- Radovic
(26, 6, 'Power Forward'),   -- Mobley (fictional)
(36, 6, 'Center'),          -- Traore

-- Warriors Traditional Q3
(3, 7, 'Point Guard'),      -- Curry
(32, 7, 'Shooting Guard'),  -- Flagg
(25, 7, 'Small Forward'),   -- Franz
(31, 7, 'Power Forward'),   -- Tucker
(23, 7, 'Center'),          -- Sengun

-- Warriors Switch Everything Q4
(3, 8, 'Point Guard'),      -- Curry
(32, 8, 'Shooting Guard'),  -- Flagg
(38, 8, 'Small Forward'),   -- Radovic
(25, 8, 'Power Forward'),   -- Franz
(26, 8, 'Center'),          -- Mobley

-- Lakers Lineups (lineup_id 9-11)
-- Lakers Starting 5 Q1
(2, 9, 'Small Forward'),    -- LeBron
(14, 9, 'Power Forward'),   -- AD
(30, 9, 'Point Guard'),     -- Lowry
(18, 9, 'Shooting Guard'),  -- Booker (fictional)
(28, 9, 'Center'),          -- Rob Williams

-- Lakers Bench Q2
(17, 10, 'Point Guard'),    -- Mitchell (fictional)
(19, 10, 'Shooting Guard'), -- Herro (fictional)
(27, 10, 'Small Forward'),  -- Smart (fictional)
(24, 10, 'Power Forward'),  -- Barnes (fictional)
(23, 10, 'Center'),         -- Sengun (fictional)

-- Lakers Clutch Q3
(2, 11, 'Point Guard'),     -- LeBron
(14, 11, 'Center'),         -- AD at center
(18, 11, 'Shooting Guard'), -- Booker
(17, 11, 'Small Forward'),  -- Mitchell
(27, 11, 'Power Forward'),  -- Smart

-- Celtics Lineups (lineup_id 12-15)
-- Celtics Starting Q1
(8, 12, 'Small Forward'),   -- Tatum
(29, 12, 'Point Guard'),    -- White
(27, 12, 'Shooting Guard'), -- Smart
(28, 12, 'Power Forward'),  -- Rob Williams
(26, 12, 'Center'),         -- Mobley (fictional)

-- Celtics Bench Q2
(33, 13, 'Point Guard'),    -- Harper (fictional)
(22, 13, 'Shooting Guard'), -- Green (fictional)
(34, 13, 'Small Forward'),  -- Bailey (fictional)
(21, 13, 'Power Forward'),  -- OG (fictional)
(36, 13, 'Center'),         -- Traore

-- Celtics Switch Q3
(8, 14, 'Power Forward'),   -- Tatum at 4
(29, 14, 'Point Guard'),    -- White
(20, 14, 'Shooting Guard'), -- Mikal (fictional)
(27, 14, 'Small Forward'),  -- Smart
(28, 14, 'Center'),         -- Rob Williams

-- Celtics Death Lineup Q4
(8, 15, 'Small Forward'),   -- Tatum
(29, 15, 'Point Guard'),    -- White
(27, 15, 'Shooting Guard'), -- Smart
(21, 15, 'Power Forward'),  -- OG
(20, 15, 'Center'),         -- Mikal at center

-- Heat Lineups (lineup_id 16-18)
-- Heat Starting Q1
(10, 16, 'Small Forward'),  -- Butler
(19, 16, 'Shooting Guard'), -- Herro
(30, 16, 'Point Guard'),    -- Lowry
(31, 16, 'Power Forward'),  -- Tucker
(23, 16, 'Center'),         -- Sengun (fictional)

-- Heat Zone Q2
(35, 17, 'Point Guard'),    -- Edgecombe
(22, 17, 'Shooting Guard'), -- Green (fictional)
(34, 17, 'Small Forward'),  -- Bailey (fictional)
(24, 17, 'Power Forward'),  -- Barnes (fictional)
(36, 17, 'Center'),         -- Traore

-- Heat Clutch Q3
(10, 18, 'Point Guard'),    -- Butler
(19, 18, 'Shooting Guard'), -- Herro
(27, 18, 'Small Forward'),  -- Smart (fictional)
(31, 18, 'Power Forward'),  -- Tucker
(28, 18, 'Center'),         -- Rob Williams (fictional)

-- 76ers Lineups (lineup_id 19-20)
-- 76ers Traditional Q1
(6, 19, 'Center'),          -- Embiid
(34, 19, 'Small Forward'),  -- Bailey
(17, 19, 'Point Guard'),    -- Mitchell (fictional)
(18, 19, 'Shooting Guard'), -- Booker (fictional)
(26, 19, 'Power Forward'),  -- Mobley (fictional)

-- 76ers Small Ball Q2
(6, 20, 'Center'),          -- Embiid
(8, 20, 'Power Forward'),   -- Tatum (fictional)
(33, 20, 'Point Guard'),    -- Harper
(20, 20, 'Shooting Guard'), -- Mikal
(25, 20, 'Small Forward'),  -- Franz

-- Mavs Lineups (lineup_id 21-24)
-- Mavs Starting Q1
(7, 21, 'Point Guard'),     -- Luka
(18, 21, 'Shooting Guard'), -- Booker (fictional)
(25, 21, 'Small Forward'),  -- Franz (fictional)
(26, 21, 'Power Forward'),  -- Mobley (fictional)
(23, 21, 'Center'),         -- Sengun (fictional)

-- Mavs Bench Q2  
(37, 22, 'Point Guard'),    -- Hugo
(22, 22, 'Shooting Guard'), -- Green
(38, 22, 'Small Forward'),  -- Radovic
(31, 22, 'Power Forward'),  -- Tucker
(36, 22, 'Center'),         -- Traore

-- Mavs Spacing Q3
(7, 23, 'Point Guard'),     -- Luka
(32, 23, 'Shooting Guard'), -- Flagg (fictional)
(25, 23, 'Small Forward'),  -- Franz
(20, 23, 'Power Forward'),  -- Mikal
(28, 23, 'Center'),         -- Rob Williams

-- Mavs Clutch Q4
(7, 24, 'Point Guard'),     -- Luka
(18, 24, 'Shooting Guard'), -- Booker
(1, 24, 'Small Forward'),   -- KD (fictional trade)
(21, 24, 'Power Forward'),  -- OG
(26, 24, 'Center'),         -- Mobley

-- Suns Lineups (lineup_id 25-26)
-- Suns Starting Q1
(18, 25, 'Shooting Guard'), -- Booker
(17, 25, 'Point Guard'),    -- Mitchell (fictional)
(1, 25, 'Small Forward'),   -- KD (fictional)
(14, 25, 'Power Forward'),  -- AD (fictional)
(6, 25, 'Center'),          -- Embiid (fictional)

-- Suns Bench Q2
(35, 26, 'Point Guard'),    -- Edgecombe
(19, 26, 'Shooting Guard'), -- Herro (fictional)
(34, 26, 'Small Forward'),  -- Bailey
(24, 26, 'Power Forward'),  -- Barnes
(36, 26, 'Center'),         -- Traore

-- Hawks Lineups (lineup_id 27-29)
-- Hawks Starting Q1
(16, 27, 'Point Guard'),    -- Trae
(22, 27, 'Shooting Guard'), -- Green (fictional)
(25, 27, 'Small Forward'),  -- Franz (fictional)
(24, 27, 'Power Forward'),  -- Barnes (fictional)
(23, 27, 'Center'),         -- Sengun (fictional)

-- Hawks Bench Q2
(37, 28, 'Point Guard'),    -- Hugo
(35, 28, 'Shooting Guard'), -- Edgecombe
(38, 28, 'Small Forward'),  -- Radovic
(31, 28, 'Power Forward'),  -- Tucker
(36, 28, 'Center'),         -- Traore

-- Hawks Small Ball Q3
(16, 29, 'Point Guard'),    -- Trae
(19, 29, 'Shooting Guard'), -- Herro (fictional)
(27, 29, 'Small Forward'),  -- Smart (fictional)
(20, 29, 'Power Forward'),  -- Mikal
(21, 29, 'Center'),         -- OG at center

-- Bucks Lineups (lineup_id 30-32)  
-- Bucks Starting Q1
(5, 30, 'Power Forward'),   -- Giannis
(13, 30, 'Point Guard'),    -- Dame
(17, 30, 'Shooting Guard'), -- Mitchell (fictional)
(20, 30, 'Small Forward'),  -- Mikal (fictional)
(28, 30, 'Center'),         -- Rob Williams

-- Bucks Bench Q2
(30, 31, 'Point Guard'),    -- Lowry
(22, 31, 'Shooting Guard'), -- Green
(38, 31, 'Small Forward'),  -- Radovic
(24, 31, 'Power Forward'),  -- Barnes
(26, 31, 'Center'),         -- Mobley

-- Bucks Death Lineup Q3
(5, 32, 'Center'),          -- Giannis at center
(13, 32, 'Point Guard'),    -- Dame
(17, 32, 'Shooting Guard'), -- Mitchell
(21, 32, 'Small Forward'),  -- OG
(20, 32, 'Power Forward'),  -- Mikal

-- Knicks Lineups (lineup_id 35-36)
-- Knicks Starting Q1
(33, 35, 'Point Guard'),    -- Harper
(29, 35, 'Shooting Guard'), -- White (fictional)
(20, 35, 'Small Forward'),  -- Mikal
(21, 35, 'Power Forward'),  -- OG  
(26, 35, 'Center'),         -- Mobley (fictional)

-- Knicks Bench Q2
(37, 36, 'Point Guard'),    -- Hugo
(35, 36, 'Shooting Guard'), -- Edgecombe
(34, 36, 'Small Forward'),  -- Bailey
(31, 36, 'Power Forward'),  -- Tucker
(36, 36, 'Center'),         -- Traore

-- Thunder Lineups (lineup_id 33-34) - adding these
-- Thunder Starting Q1
(17, 33, 'Shooting Guard'), -- Mitchell (fictional assignment)
(37, 33, 'Point Guard'),    -- Hugo
(25, 33, 'Small Forward'),  -- Franz (fictional)
(24, 33, 'Power Forward'),  -- Barnes (fictional)
(26, 33, 'Center'),         -- Mobley (fictional)

-- Thunder Bench Q2  
(35, 34, 'Point Guard'),    -- Edgecombe
(22, 34, 'Shooting Guard'), -- Green
(38, 34, 'Small Forward'),  -- Radovic
(31, 34, 'Power Forward'),  -- Tucker
(36, 34, 'Center'),         -- Traore;