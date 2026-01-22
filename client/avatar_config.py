# client/avatar_config.py
import os

# Danh sách tên file ảnh của bạn
AVATAR_FILENAMES = [
    "icons8_alien_96px.png",
    "icons8_angry_face_meme_96px.png",
    "icons8_animation_96px.png",
    "icons8_avatar_96px.png",
    "icons8_bad_piggies_96px.png",
    "icons8_bendy_96px.png",
    "icons8_captain_america_96px.png",
    "icons8_crash_bandicoot_96px.png",
    "icons8_deadpool_96px.png",
    "icons8_elektrovieh_96px.png",
    "icons8_gandalf_96px.png",
    "icons8_ghost_96px.png",
    "icons8_groot_96px.png",
    "icons8_hinata_96px.png",
    "icons8_hulk_96px.png",
    "icons8_ignore_96px.png",
    "icons8_iron_man_96px.png",
    "icons8_jake_96px.png",
    "icons8_jetpack_joyride_96px.png",
    "icons8_joker_dc_96px.png",
    "icons8_logan_x_men_96px.png",
    "icons8_magneto_96px.png",
    "icons8_minecraft_main_character_96px.png",
    "icons8_minecraft_skeleton_96px.png",
    "icons8_minecraft_zombie_96px.png",
    "icons8_morpheus_96px.png",
    "icons8_naruto_96px.png",
    "icons8_neo_96px.png",
    "icons8_orc_96px.png",
    "icons8_pelican_96px.png",
    "icons8_pennywise_96px.png",
    "icons8_pikachu_pokemon_96px.png",
    "icons8_rick_sanchez_96px.png",
    "icons8_sailor_moon_96px.png",
    "icons8_sasuke_uchiha_96px.png",
    "icons8_sonic_the_hedgehog_96px.png",
    "icons8_spider-man_head_96px.png",
    "icons8_steven_universe_96px.png",
    "icons8_super_mario_96px.png",
    "icons8_the_flash_head_96px.png",
    "icons8_transformer_96px.png",
    "icons8_trinity_96px.png",
    "icons8_venom_head_96px.png",
    "icons8_vietnam_96px.png",
    "icons8_year_of_rooster_96px.png",
    "icons8_saitama_96px.png",
    "icons8_trollface_96px.png"
]

def get_avatar_path(index):
    """Lấy đường dẫn file ảnh dựa trên ID (index)"""
    # Ép kiểu int để tránh lỗi
    try:
        idx = int(index)
    except (ValueError, TypeError):
        idx = 0  # Default to 0 if conversion fails

    # Safety logic: If the index is out of bounds, use modulo to wrap around
    if AVATAR_FILENAMES:
        safe_idx = idx % len(AVATAR_FILENAMES)
        filename = AVATAR_FILENAMES[safe_idx]
        return os.path.join("assets", "avatar", filename)
    
    # Fallback cuối cùng nếu list rỗng
    return ""
