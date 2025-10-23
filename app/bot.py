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
    
    embed.add_field(name="$주제추첨 [옵션]", 
                    value="주제 목록에서 7개의 주제를 무작위로 추첨합니다.\n"
                          "- `제외:[정확도]` : 특정 정확도를 제외합니다. 여러 개일 경우 쉼표(,)로 구분합니다. (e.g. `제외:D,F`)\n"
                          "- `난이도:[숫자]` : 특정 난이도 이상의 주제만 추첨합니다. (e.g. `난이도:1.5`)\n"
                          "- 예시: `$주제추첨 제외:F 난이도:2` (F등급 제외, 난이도 2 이상)",
                    inline=False)
    
    admin_commands = (
        "**DB 관리 명령어 (관리자 전용)**\n"
        "`$추가 <이름> <난이도> <정확도>`: 새 주제를 추가합니다.\n"
        "   - 예: `$추가 \"새 주제\" 4.5 A`\n"
        "`$제거 <이름>`: 기존 주제를 제거합니다.\n"
        "   - 예: `$제거 \"오래된 주제\"`\n"
        "`$수정 <이름> <항목> <값>`: 주제 정보를 수정합니다.\n"
        "   - 항목: `name`, `diff`, `acc`\n"
        "   - 예: `$수정 \"기존 주제\" diff 5.0`"
    )
    embed.add_field(name="관리자 명령어", value=admin_commands, inline=False)

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
# data.py에 데이터를 저장하는 함수
def save_data():
    with open('app/data.py', 'w', encoding='utf-8') as f:
        f.write('theme_list = [\n')
        for theme in theme_list:
            f.write(f'    {{\n        "theme": "{theme["theme"]}", \n        "difficulty": {theme["difficulty"]}, \n        "accuracy": "{theme["accuracy"]}"\n    }},\n')
        f.write(']\n')

# DB 관리를 위한 명령어
@bot.command(name='추가')
@commands.has_permissions(administrator=True)
async def add_theme(ctx, name: str, diff_value: float, acc_value: str):
    """새로운 주제를 DB에 추가합니다. (관리자용)"""
    # Check if theme already exists
    for theme in theme_list:
        if theme['theme'] == name:
            await ctx.send(f"'{name}' 주제는 이미 존재합니다.")
            return
            
    new_theme = {"theme": name, "difficulty": diff_value, "accuracy": acc_value.upper()}
    theme_list.append(new_theme)
    save_data()
    await ctx.send(f"'{name}' 주제를 추가했습니다.")

@add_theme.error
async def add_theme_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("이 명령어를 사용할 권한이 없습니다.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("사용법: $추가 <이름> <난이도> <정확도>")
    else:
        await ctx.send(f"오류가 발생했습니다: {error}")

@bot.command(name='제거')
@commands.has_permissions(administrator=True)
async def remove_theme(ctx, *, name: str):
    """주제를 DB에서 제거합니다. (관리자용)"""
    theme_to_remove = None
    for theme in theme_list:
        if theme['theme'] == name:
            theme_to_remove = theme
            break
    
    if theme_to_remove:
        theme_list.remove(theme_to_remove)
        save_data()
        await ctx.send(f"'{name}' 주제를 제거했습니다.")
    else:
        await ctx.send(f"'{name}' 주제를 찾을 수 없습니다.")

@remove_theme.error
async def remove_theme_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("이 명령어를 사용할 권한이 없습니다.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("사용법: $제거 <이름>")
    else:
        await ctx.send(f"오류가 발생했습니다: {error}")

@bot.command(name='수정')
@commands.has_permissions(administrator=True)
async def edit_theme(ctx, name: str, field: str, *, value: str):
    """주제의 정보를 수정합니다. (관리자용)"""
    theme_to_edit = None
    for theme in theme_list:
        if theme['theme'] == name:
            theme_to_edit = theme
            break

    if not theme_to_edit:
        await ctx.send(f"'{name}' 주제를 찾을 수 없습니다.")
        return

    field = field.lower()
    if field in ['diff', 'difficulty']:
        try:
            theme_to_edit['difficulty'] = float(value)
            save_data()
            await ctx.send(f"'{name}' 주제의 난이도를 {value}로 수정했습니다.")
        except ValueError:
            await ctx.send("난이도는 숫자여야 합니다.")
    elif field in ['acc', 'accuracy']:
        theme_to_edit['accuracy'] = value.upper()
        save_data()
        await ctx.send(f"'{name}' 주제의 정확도를 {value.upper()}로 수정했습니다.")
    elif field in ['name', 'theme']:
        # Check if new name already exists
        for theme in theme_list:
            if theme['theme'] == value:
                await ctx.send(f"'{value}' 주제는 이미 존재합니다.")
                return
        theme_to_edit['theme'] = value
        save_data()
        await ctx.send(f"'{name}' 주제의 이름을 {value}로 수정했습니다.")
    else:
        await ctx.send("수정할 수 있는 항목은 'name', 'diff', 'acc' 입니다.")

@edit_theme.error
async def edit_theme_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("이 명령어를 사용할 권한이 없습니다.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("사용법: $수정 <이름> <항목(name/diff/acc)> <값>")
    else:
        await ctx.send(f"오류가 발생했습니다: {error}")

if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("봇 토큰이 설정되지 않았습니다. BOT_TOKEN 변수에 봇의 토큰을 입력해주세요.")
