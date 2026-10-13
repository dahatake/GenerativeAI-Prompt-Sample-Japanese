-- 研修用の架空データ。Azure SQL Database 用。プロトタイプ/sample の「13/14」向け。実在店舗とは無関係です。
DROP TABLE IF EXISTS route_options; DROP TABLE IF EXISTS restaurants; DROP TABLE IF EXISTS tourist_spots; DROP TABLE IF EXISTS payment_methods;
GO
CREATE TABLE payment_methods (payment_method_id nvarchar(10) PRIMARY KEY, name nvarchar(50) NOT NULL, is_cashless bit NOT NULL, created_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME(), updated_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME());
CREATE TABLE restaurants (restaurant_id nvarchar(10) PRIMARY KEY, name nvarchar(100) NOT NULL, area nvarchar(20) NOT NULL, area_code nvarchar(10) NOT NULL, category nvarchar(30) NOT NULL, supports_cashless bit NOT NULL, open_from time NOT NULL, open_to time NOT NULL, avg_price_yen int NOT NULL, favorite_count int NOT NULL, review_score decimal(2,1) NOT NULL, payment_method_ids nvarchar(100) NOT NULL, latitude float NOT NULL, longitude float NOT NULL, created_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME(), updated_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME());
CREATE TABLE tourist_spots (spot_id nvarchar(10) PRIMARY KEY, name nvarchar(100) NOT NULL, area_code nvarchar(10) NOT NULL, tags nvarchar(100) NOT NULL, rain_note nvarchar(30) NOT NULL, admission_yen int NOT NULL, latitude float NOT NULL, longitude float NOT NULL, created_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME(), updated_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME());
CREATE TABLE route_options (route_id nvarchar(10) PRIMARY KEY, origin nvarchar(50) NOT NULL, destination nvarchar(100) NOT NULL, mode nvarchar(20) NOT NULL, minutes int NOT NULL, fare_yen int NOT NULL, created_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME(), updated_at datetime2 NOT NULL DEFAULT SYSUTCDATETIME());
GO
INSERT INTO payment_methods (payment_method_id, name, is_cashless) VALUES
(N'PAY-01', N'現金', 0),
(N'PAY-02', N'クレジットカード', 1),
(N'PAY-03', N'交通系IC', 1),
(N'PAY-04', N'QRコード決済', 1),
(N'PAY-05', N'電子マネー(流通系)', 1);
INSERT INTO restaurants (restaurant_id, name, area, area_code, category, supports_cashless, open_from, open_to, avg_price_yen, favorite_count, review_score, payment_method_ids, latitude, longitude) VALUES
(N'RST-001', N'ミルクボックスカフェ郡山駅前', N'駅前', N'EKI', N'カフェ', 1, '08:00', '20:00', 1200, 412, 4.3, N'PAY-02,PAY-03', 37.3982, 140.388),
(N'RST-002', N'磐梯山味噌ラーメン 麓', N'湖南', N'KONAN', N'ラーメン', 1, '11:00', '21:00', 980, 655, 4.5, N'PAY-01,PAY-04', 37.432, 140.217),
(N'RST-003', N'駅前酒場 あさか屋', N'駅前', N'EKI', N'居酒屋', 1, '17:00', '23:30', 3800, 288, 4.1, N'PAY-01,PAY-02,PAY-04', 37.3991, 140.3871),
(N'RST-004', N'麓山そば処 山並', N'開成山', N'KAISEI', N'そば', 0, '11:00', '15:00', 1100, 201, 4.4, N'PAY-01', 37.4028, 140.3665),
(N'RST-005', N'こおりやま鯉ごはん 水辺', N'安積', N'ASAKA', N'和食', 1, '11:30', '21:00', 2400, 340, 4.0, N'PAY-02,PAY-03,PAY-05', 37.3735, 140.349),
(N'RST-006', N'カフェ・ド・ふくしま 朝市', N'駅前', N'EKI', N'カフェ', 1, '07:00', '17:00', 900, 175, 3.9, N'PAY-02,PAY-03,PAY-04', 37.3975, 140.3895),
(N'RST-007', N'ぶどうの丘ベーカリー', N'湖南', N'KONAN', N'パン', 0, '09:00', '17:30', 650, 120, 4.2, N'PAY-01,PAY-05', 37.441, 140.2255),
(N'RST-008', N'うまか鶏 駅前本店', N'駅前', N'EKI', N'焼き鳥', 1, '16:30', '23:00', 3200, 530, 4.2, N'PAY-01,PAY-02,PAY-04', 37.3988, 140.386),
(N'RST-009', N'ふるさと郷土料理 いなほ庵', N'安積', N'ASAKA', N'郷土料理', 1, '11:00', '20:30', 2800, 410, 4.6, N'PAY-02,PAY-03', 37.371, 140.3522),
(N'RST-010', N'夜景テラス 逢瀬ビュー', N'逢瀬', N'OUSE', N'ダイニング', 1, '17:00', '22:00', 4500, 96, 3.8, N'PAY-02,PAY-04', 37.356, 140.401);
INSERT INTO tourist_spots (spot_id, name, area_code, tags, rain_note, admission_yen, latitude, longitude) VALUES
(N'SPT-001', N'開成山公園', N'KAISEI', N'自然,散策,家族向け', N'雨天不可', 0, 37.4012, 140.3641),
(N'SPT-002', N'安積歴史博物館', N'ASAKA', N'歴史,雨天可', N'雨天可', 600, 37.3705, 140.3501),
(N'SPT-003', N'麓山展望台', N'KAISEI', N'夜景,自然', N'雨天不可', 0, 37.4105, 140.359),
(N'SPT-004', N'湖南みどり体験農園', N'KONAN', N'体験,自然,家族向け', N'雨天可(一部)', 1500, 37.445, 140.23),
(N'SPT-005', N'水路めぐり遊歩道', N'ASAKA', N'散策,歴史', N'雨天不可', 0, 37.369, 140.347),
(N'SPT-006', N'旧酒蔵ギャラリー', N'ASAKA', N'歴史,雨天可,体験', N'雨天可', 800, 37.372, 140.351),
(N'SPT-007', N'逢瀬の丘 夜景スポット', N'OUSE', N'夜景,自然', N'雨天不可', 0, 37.355, 140.402),
(N'SPT-008', N'こおりやま陶芸工房', N'EKI', N'体験,雨天可', N'雨天可', 2800, 37.396, 140.392);
INSERT INTO route_options (route_id, origin, destination, mode, minutes, fare_yen) VALUES
(N'RTE-001', N'郡山駅', N'開成山公園', N'バス', 15, 240),
(N'RTE-002', N'郡山駅', N'開成山公園', N'徒歩', 35, 0),
(N'RTE-003', N'郡山駅', N'開成山公園', N'タクシー', 12, 1800),
(N'RTE-004', N'郡山駅', N'安積歴史博物館', N'バス', 22, 240),
(N'RTE-005', N'郡山駅', N'麓山展望台', N'バス', 20, 240),
(N'RTE-006', N'郡山駅', N'麓山展望台', N'タクシー', 14, 2000),
(N'RTE-007', N'郡山駅', N'湖南みどり体験農園', N'バス', 48, 520),
(N'RTE-008', N'郡山駅', N'逢瀬の丘 夜景スポット', N'タクシー', 25, 3600),
(N'RTE-009', N'郡山駅', N'こおりやま陶芸工房', N'徒歩', 12, 0),
(N'RTE-010', N'開成山公園', N'麓山展望台', N'徒歩', 18, 0),
(N'RTE-011', N'安積歴史博物館', N'水路めぐり遊歩道', N'徒歩', 8, 0),
(N'RTE-012', N'郡山駅', N'旧酒蔵ギャラリー', N'バス', 24, 240);
GO
-- 人気レストラン(22. サンプルクエリ): favorite_count 最大、同率は review_score 降順
SELECT TOP 1 name, favorite_count, review_score FROM restaurants ORDER BY favorite_count DESC, review_score DESC;
