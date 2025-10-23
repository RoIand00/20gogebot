import discord
from discord.ext import commands
import random
import re
from data import theme_list

BOT_TOKEN = ""

# Bot 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="$도움말을 사용해 명령어를 알아보세요!"))
    print(f'{bot.user.name}이(가) 성공적으로 로그인했습니다. (ID: {bot.user.id})')

@bot.command(name='도움말')
async def help_command(ctx):
    """봇의 명령어 목록과 사용법을 보여줍니다."""
    embed = discord.Embed(title="🎲 스무고개 봇 도움말", description="스무고개 봇의 명령어 목록입니다.", color=discord.Color.blue())
    
    embed.add_field(name="!주제추첨 [옵션]", 
                    value="주제 목록에서 7개의 주제를 무작위로 추첨합니다.\n"
                          "- `제외:[정확도]` : 특정 정확도를 제외합니다. 여러 개일 경우 쉼표(,)로 구분합니다. (e.g. `제외:D,F`)\n"
                          "- `난이도:[숫자]` : 특정 난이도 이상의 주제만 추첨합니다. (e.g. `난이도:1.5`)\n"
                          "- 예시: `!주제추첨 제외:F 난이도:2` (F등급 제외, 난이도 2 이상)",
                    inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='주제추첨')
async def theme_selection(ctx, *, args: str = None):
    """
    주제 목록에서 7개의 주제를 무작위로 추첨합니다.
    키워드 인수를 사용하여 특정 정확도를 제외하거나 최소 난이도를 설정할 수 있습니다.
    """
    try:
        filtered_themes = theme_list
        제외할_정확도_str = None
        최소_난이도 = None

        if args:
            exclude_match = re.search(r"제외:([A-DFa-df,]+)", args, re.IGNORECASE)
            difficulty_match = re.search(r"난이도:([0-9.]+)", args, re.IGNORECASE)

            if exclude_match:
                제외할_정확도_str = exclude_match.group(1)

            if difficulty_match:
                try:
                    최소_난이도 = float(difficulty_match.group(1))
                except ValueError:
                    await ctx.send("난이도 값은 숫자여야 합니다.")
                    return

        if 제외할_정확도_str:
            excluded_accuracies = [acc.strip().upper() for acc in 제외할_정확도_str.split(',')]
            invalid_accuracies = [acc for acc in excluded_accuracies if acc not in ['A', 'B', 'C', 'D', 'F']]
            if invalid_accuracies:
                await ctx.send(f"잘못된 정확도 값이 포함되어 있습니다: {', '.join(invalid_accuracies)}")
                return
            
            filtered_themes = [theme for theme in filtered_themes if theme.get('accuracy') not in excluded_accuracies]

        if 최소_난이도 is not None:
            filtered_themes = [theme for theme in filtered_themes if theme.get('difficulty', 0) >= 최소_난이도]

        if len(filtered_themes) < 7:
            await ctx.send("추첨할 수 있는 주제가 7개 미만입니다.")
            return

        selected_themes = random.sample(filtered_themes, 7)
        selected_themes.sort(key=lambda x: x.get('difficulty', 0))
        
        response = "🎲 주제 추첨 결과 🎲\n\n"
        for i, theme in enumerate(selected_themes):
            response += f"{i + 1}. **{theme['theme']}** 주제가 나왔습니다. (난이도: {theme['difficulty']}, 정확도: {theme['accuracy']})\n"
        
        await ctx.send(response)

    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {e}")

# 봇 실행
if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("봇 토큰이 설정되지 않았습니다. BOT_TOKEN 변수에 봇의 토큰을 입력해주세요.")
