import discord
from discord.ext import commands
import random
from data import theme_list

# 봇의 토큰을 넣는 변수
BOT_TOKEN = "MTMzMjI0Njg5NzY4Mjk0NDAyMg.GJ4zmS.WaP9LyCAIkmyerG4KF8BE-5y9H3RoRoib29LmM"

# Bot 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user.name}이(가) 성공적으로 로그인했습니다. (ID: {bot.user.id})')

@bot.command(name='도움말')
async def help_command(ctx):
    """봇의 명령어 목록과 사용법을 보여줍니다."""
    embed = discord.Embed(title="🎲 스무고개 봇 도움말", description="스무고개 봇의 명령어 목록입니다.", color=discord.Color.blue())
    
    embed.add_field(name="!주제추첨 [제외할 정확도] [최소 난이도]", value="주제 목록에서 7개의 주제를 무작위로 추첨합니다.\n- `[제외할 정확도]`는 선택적으로 입력할 수 있으며, 여러 개를 입력할 수 있습니다. (A, B, C, D, F)\n- `[최소 난이도]`는 선택적으로 입력할 수 있습니다.\n- 예시 1: `!주제추첨 F` (F등급 정확도 주제 제외)\n- 예시 2: `!주제추첨 D F` (D, F등급 정확도 주제 제외)\n- 예시 3: `!주제추첨 1.5` (난이도 1.5 이상인 주제만 추첨)\n- 예시 4: `!주제추첨 F 1.5` (F등급을 제외하고 난이도 1.5 이상인 주제만 추첨)", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='주제추첨')
async def theme_selection(ctx, *args):
    """
    주제 목록에서 7개의 주제를 무작위로 추첨합니다.
    특정 정확도를 제외하거나 최소 난이도를 설정할 수 있습니다.
    """
    try:
        제외할_정확도들 = []
        최소_난이도 = 0.0

        for arg in args:
            arg = arg.upper()
            if arg in ['A', 'B', 'C', 'D', 'F']:
                제외할_정확도들.append(arg)
            else:
                try:
                    최소_난이도 = float(arg)
                except ValueError:
                    await ctx.send(f"'{arg}'는 잘못된 인수입니다. 정확도(A, B, C, D, F) 또는 숫자를 입력해주세요.")
                    return

        filtered_themes = theme_list
        if 제외할_정확도들:
            filtered_themes = [theme for theme in filtered_themes if theme.get('accuracy') not in 제외할_정확도들]

        if 최소_난이도 > 0:
            filtered_themes = [theme for theme in filtered_themes if theme.get('difficulty', 0) >= 최소_난이도]

        if len(filtered_themes) < 7:
            await ctx.send("추첨할 수 있는 주제가 7개 미만입니다.")
            return

        selected_themes = random.sample(filtered_themes, 7)
        selected_themes.sort(key=lambda x: x.get('difficulty', 0))
        
        response = "🎲 주제 추첨 결과 🎲\n\n" 
        for i, theme in enumerate(selected_themes):
            response += f"{i + 1}. **{theme['theme']}** 주제가 나왔습니다. (난이도: {theme['difficulty']})\n"
        
        await ctx.send(response)

    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {e}")

# 봇 실행
if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("봇 토큰이 설정되지 않았습니다. BOT_TOKEN 변수에 봇의 토큰을 입력해주세요.")
