-- ユーザーテーブルの作成
CREATE TABLE Users (
    UserId NVARCHAR(50) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Email NVARCHAR(255) NOT NULL UNIQUE
);

-- 観光スポットテーブルの作成
CREATE TABLE Spots (
    SpotId NVARCHAR(50) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(MAX) NOT NULL,
    Category NVARCHAR(50),
    Longitude FLOAT,
    Latitude FLOAT
);

-- グルメ情報テーブルの作成
CREATE TABLE Restaurants (
    SpotId NVARCHAR(50) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(MAX) NOT NULL,
    Category NVARCHAR(50),
    Longitude FLOAT,
    Latitude FLOAT
);

-- 予約テーブルの作成
CREATE TABLE Reservations (
    ReservationId NVARCHAR(50) PRIMARY KEY,
    UserId NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES Users(UserId),
    SpotId NVARCHAR(50) NOT NULL,
    ReservationDate DATE NOT NULL,
    Status NVARCHAR(50) NOT NULL
);

-- レビューテーブルの作成
CREATE TABLE Reviews (
    ReviewId NVARCHAR(50) PRIMARY KEY,
    SpotId NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES Spots(SpotId),
    UserId NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES Users(UserId),
    ReviewDate DATE NOT NULL,
    Rating INT NOT NULL,
    Comment NVARCHAR(MAX)
);

-- 支払い情報テーブルの作成
CREATE TABLE Payments (
    PaymentId NVARCHAR(50) PRIMARY KEY,
    ReservationId NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES Reservations(ReservationId),
    Amount FLOAT NOT NULL,
    Method NVARCHAR(50) NOT NULL,
    PaymentDate DATE NOT NULL,
    Status NVARCHAR(50) NOT NULL
);
