import discord
from discord.ext import commands
from discord import app_commands
import json
import os

TOKEN = os.getenv("TOKEN")

histoire_active = {
    "active": False,
    "titre": "",
    "texte": ""
}

SALON_HISTOIRES = 1525568008724938822

FICHIER_HISTOIRE = "histoire.json"


def sauvegarder_histoire():

    with open(FICHIER_HISTOIRE, "w", encoding="utf-8") as f:
        json.dump(
            histoire_active,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("💾 Histoire sauvegardée !")

def charger_histoire():

    global histoire_active

    if os.path.exists(FICHIER_HISTOIRE):

        with open(FICHIER_HISTOIRE, "r", encoding="utf-8") as f:
            histoire_active = json.load(f)

        print("📖 Histoire chargée !")

    else:
        print("📖 Aucune histoire sauvegardée.")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():

    charger_histoire()

    await bot.tree.sync()

    print(f"{bot.user} est connectée !")


lucy = app_commands.Group(
    name="lucy",
    description="Commandes de Lucy"
)

bot.tree.add_command(lucy)

class HistoireForm(discord.ui.Modal, title="Nouvelle aventure"):

    titre = discord.ui.TextInput(
        label="Titre de l'histoire",
        placeholder="Ex : Le gâteau disparu d'Erza",
        required=False
    )

    debut = discord.ui.TextInput(
        label="Début de l'histoire",
        placeholder="Écris le début de l'aventure...",
        style=discord.TextStyle.paragraph,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):

        histoire_active["active"] = True
        histoire_active["titre"] = self.titre.value
        histoire_active["texte"] = self.debut.value

        sauvegarder_histoire()

        salon = interaction.guild.get_channel(SALON_HISTOIRES)

        await salon.send(
            f"📖 **{self.titre.value}**\n\n"
            f"{self.debut.value}"
        )

        await interaction.response.send_message(
            "✅ L'histoire commence !",
            ephemeral=True
        )

@lucy.command(
    name="start",
    description="Commencer une nouvelle histoire"
)
async def start(interaction: discord.Interaction):
       
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "❌ Tu n'as pas la permission d'utiliser Lucy.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(HistoireForm())

@lucy.command(
    name="end",
    description="Terminer l'histoire actuelle"
)
async def end(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "❌ Tu n'as pas la permission d'utiliser Lucy.",
            ephemeral=True
        )
        return

    if not histoire_active["active"]:
        await interaction.response.send_message(
            "❌ Aucune histoire n'est en cours.",
            ephemeral=True
        )
        return


    salon = interaction.guild.get_channel(SALON_HISTOIRES)


    await salon.send(
    f"━━━━━━━━━━━━━━━\n"
    f"📖 **{histoire_active['titre']}**\n"
    f"━━━━━━━━━━━━━━━\n\n"
    f"{histoire_active['texte']}\n\n"
    f"✨ *Un nouveau chapitre ajouté au livre de Lucy* 📖✨"
)


    histoire_active["active"] = False
    histoire_active["titre"] = ""
    histoire_active["texte"] = ""


    await interaction.response.send_message(
        "✅ L'histoire est terminée !",
        ephemeral=True
    )

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if histoire_active["active"]:

        histoire_active["texte"] += "\n" + message.content.strip()

        print("Message ajouté à l'histoire :", message.content)

    await bot.process_commands(message)


bot.run(TOKEN)

