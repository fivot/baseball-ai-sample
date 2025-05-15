from dataclasses import dataclass
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time

# 結果の構造
@dataclass
class GameResult:
    team_name: str
    won: bool

# メイン処理クラス
class Job:
    def __init__(self):
        pass

    def execute(self, url: str):
        self.exec_by_openai(url)

    def exec_by_openai(self, url: str):
        options = Options()
        options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())

        try:
            driver = webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            print("Selenium起動に失敗:", e)
            return

        try:
            driver.get(url)
            time.sleep(3)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
        finally:
            driver.quit()

        results = []

        games = soup.select("li.bb-score__item")
        print(f"試合数: {len(games)}")

        for game in games:
            home_team_elem = game.select_one("p.bb-score__homeLogo")
            away_team_elem = game.select_one("p.bb-score__awayLogo")
            score_left = game.select_one("span.bb-score__score--left")
            score_right = game.select_one("span.bb-score__score--right")
            status_elem = game.select_one("p.bb-score__link")  # 試合中止判定用

            # チーム名がなければスキップ
            if not home_team_elem or not away_team_elem:
                print("チーム情報が足りません")
                continue

            team1 = home_team_elem.get_text(strip=True)
            team2 = away_team_elem.get_text(strip=True)

            # スコアなし（＝中止や未開催）の場合
            if not score_left or not score_right:
                if status_elem and "中止" in status_elem.get_text(strip=True):
                    print(f"{team1} vs {team2}：試合中止")
                else:
                    print(f"{team1} vs {team2}：スコア不明（引き分け・中止・データ未掲載）")
                results.append(GameResult(team_name=team1, won=False))
                results.append(GameResult(team_name=team2, won=False))
                continue

            # 通常のスコア処理
            try:
                score1 = int(score_left.get_text(strip=True))
                score2 = int(score_right.get_text(strip=True))
                print(f"{team1} {score1} - {score2} {team2}")
            except Exception as e:
                print(f"{team1} vs {team2}：スコア読み取り失敗: {e}")
                results.append(GameResult(team_name=team1, won=False))
                results.append(GameResult(team_name=team2, won=False))
                continue

            if score1 > score2:
                results.append(GameResult(team_name=team1, won=True))
                results.append(GameResult(team_name=team2, won=False))
            elif score2 > score1:
                results.append(GameResult(team_name=team1, won=False))
                results.append(GameResult(team_name=team2, won=True))
            else:
                results.append(GameResult(team_name=team1, won=False))
                results.append(GameResult(team_name=team2, won=False))

        print("=== 試合結果 ===")
        for result in results:
            print({"team_name": result.team_name, "won": result.won})


# --- 実行部 ---
if __name__ == "__main__":
    url = "https://baseball.yahoo.co.jp/npb/schedule/?date=2025-02-12"  # 好きな日付に変えてOK
    job = Job()
    job.execute(url)
