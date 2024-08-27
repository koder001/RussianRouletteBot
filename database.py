import aiosqlite


async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect('game_data.db') as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_stats (
                    user_id INTEGER PRIMARY KEY,
                    games_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0
                )
            ''')
            await conn.commit()


async def update_game_stats(user_id, win=False):
    """Обновление статистики игры"""
    async with aiosqlite.connect('game_data.db') as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT games_played, wins, losses FROM game_stats WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()

            if row:
                games_played, wins, losses = row
                games_played += 1
                if win:
                    wins += 1
                else:
                    losses += 1
                await cursor.execute('''
                    UPDATE game_stats
                    SET games_played = ?, wins = ?, losses = ?
                    WHERE user_id = ?
                ''', (games_played, wins, losses, user_id))
            else:
                await cursor.execute('''
                    INSERT INTO game_stats (user_id, games_played, wins, losses)
                    VALUES (?, 1, ?, ?)
                ''', (user_id, 1 if win else 0, 0 if win else 1))

            await conn.commit()


async def get_user_stats(user_id):
    """Получение статистики пользователя"""
    async with aiosqlite.connect('game_data.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute('SELECT * FROM game_stats WHERE user_id = ?', (user_id,))
        stats = await cursor.fetchone()
    return stats or (0, 0, 0)


async def get_top_players():
    """Получение топ-10 игроков по количеству побед"""
    async with aiosqlite.connect('game_data.db') as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                SELECT user_id, wins
                FROM game_stats
                ORDER BY wins DESC
                LIMIT 10
            ''')
            top_players = await cursor.fetchall()
    return top_players
