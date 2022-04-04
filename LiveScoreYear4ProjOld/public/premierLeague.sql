create database IF NOT EXISTS liveScore;
use liveScore;
 
 DROP table if exists standings;
 
 create table standings (
 id integer not null primary key,
 position int not null,
 name varchar(30) not null,
 played int not null,
 win int not null,
 draw int not null,
 loss int not null,
 gfor int not null,
 gagainst int not null,
 gdiff int not null,
 points int not null);
 
 insert into standings values (49, 0, 'Chelsea', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (40, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (48, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (50, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (33, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (34, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (42, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (51, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (47, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (45, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (46, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (39, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (55, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (52, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (41, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (66, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (38, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (44, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (63, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );
 insert into standings values (71, 0, '', 0, 0, 0, 0, 0, 0, 0, 0 );

 select * from standings order by points DESC, gdiff DESC;
 
 
 
 
 DROP table if exists players;
 
 create table players (
 id integer not null primary key,
 player varchar(30) not null,
 position varchar(10) not null,
 played int not null,
 goals int not null);
 
 insert into players values (306, "", "", 0, 0);
 insert into players values (18788, "", "", 0, 0);
 insert into players values (18819, "", "", 0, 0);
 insert into players values (304, "", "", 0, 0);
 insert into players values (1496, "", "", 0, 0);
 insert into players values (1485, "", "", 0, 0);
 insert into players values (19545, "", "", 0, 0);
 insert into players values (1161, "", "", 0, 0);
 insert into players values (67972, "", "", 0, 0);
 insert into players values (1697, "", "", 0, 0);
 insert into players values (2678, "", "", 0, 0);
 insert into players values (1465, "", "", 0, 0);
 insert into players values (186, "", "", 0, 0);
 insert into players values (302, "", "", 0, 0);
 insert into players values (874, "", "", 0, 0);
 insert into players values (2218, "", "", 0, 0);
 insert into players values (897, "", "", 0, 0);
 insert into players values (24888, "", "", 0, 0);
 insert into players values (2939, "", "", 0, 0);
 insert into players values (665, "", "", 0, 0);
 
 select * from players order by goals DESC;