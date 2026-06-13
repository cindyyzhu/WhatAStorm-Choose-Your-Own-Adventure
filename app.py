from flask import Flask, render_template, session, redirect, url_for, request
import random

app = Flask(__name__)
app.secret_key = 'desert-adventure-secret-key'

# Scene metadata: background image, which images to show, text bubble image, buttons
SCENES = {
    1:  {"bg": "storm.png",      "extras": [],                          "text_img": None,              "type": "title"},
    2:  {"bg": "desert.png",     "extras": ["character.png"],           "text_img": "text_scene2.png", "type": "next"},
    3:  {"bg": "desert.png",     "extras": ["character.png"],           "text_img": "text_scene3.png", "type": "next"},
    4:  {"bg": "desert.png",     "extras": ["character.png"],           "text_img": "text_scene4.png", "type": "choices123"},
    5:  {"bg": "cave.jpg",       "extras": ["character.png"],           "text_img": "text_scene5.png", "type": "choices12"},
    6:  {"bg": None,             "extras": [],                          "text_img": "text_scene6.png", "type": "death"},
    7:  {"bg": "bridge.png",     "extras": ["character.png"],           "text_img": "text_scene7.png", "type": "choices12"},
    8:  {"bg": "bridge.png",     "extras": ["character.png"],           "text_img": "text_scene8.png", "type": "next"},
    9:  {"bg": "bridge.png",     "extras": ["character.png","troll.png"],"text_img": "text_scene9.png", "type": "choices123"},
    10: {"bg": "bridge.png",     "extras": ["character.png","troll.png"],"text_img": "text_scene10.png","type": "choices12"},
    11: {"bg": "bridge.png",     "extras": ["character.png","troll.png"],"text_img": "text_scene11.png","type": "dice"},
    12: {"bg": "city.jpg",       "extras": ["character.png"],           "text_img": "text_scene12.png","type": "victory"},
    13: {"bg": None,             "extras": [],                          "text_img": "text_scene13.png","type": "death"},
    14: {"bg": "desert.png",     "extras": ["character.png"],           "text_img": "text_scene14.png","type": "choices123"},
    15: {"bg": "cave.jpg",       "extras": ["character.png"],           "text_img": "text_scene15.png","type": "choices123"},
    16: {"bg": "insideCave.jpg", "extras": ["character.png","lion.png"],"text_img": "text_scene16.png","type": "choices12"},
    17: {"bg": None,             "extras": [],                          "text_img": "text_scene17.png","type": "death"},
    18: {"bg": "insideCave.jpg", "extras": ["character.png"],           "text_img": "text_scene18.png","type": "next"},
    19: {"bg": "insideCave.jpg", "extras": ["character.png"],           "text_img": "text_scene19.png","type": "next"},
}

# Branching logic — maps (current_scene, button) -> next_scene
# button: 'next', 'c1', 'c2', 'c3'
TRANSITIONS = {
    (1,  'next'): 2,
    (2,  'next'): 3,
    (3,  'next'): 4,
    (4,  'c1'):   5,
    (4,  'c2'):   7,
    (4,  'c3'):   14,
    (5,  'c1'):   6,   # death
    (5,  'c2'):   8,
    (7,  'c1'):   15,
    (7,  'c2'):   8,
    (8,  'next'): 9,
    (9,  'c1'):   10,
    (9,  'c2'):   13,  # death
    (9,  'c3'):   13,  # death
    (10, 'c1'):   11,  # dice roll
    (10, 'c2'):   13,  # death
    # scene 11 next handled specially (dice result)
    (14, 'c1'):   15,
    (14, 'c2'):   16,
    (14, 'c3'):   17,  # death
    (15, 'c1'):   17,  # death
    (15, 'c2'):   16,
    (15, 'c3'):   18,
    (16, 'c1'):   19,
    (16, 'c2'):   17,  # death
    (18, 'next'): 8,
    (19, 'next'): 8,
}


@app.route('/')
def index():
    session['scene'] = 1
    session['lives'] = 3
    session['dice_result'] = None
    session['dice_won'] = None
    return redirect(url_for('scene'))


@app.route('/scene')
def scene():
    scene_id = session.get('scene', 1)
    lives = session.get('lives', 3)
    dice_result = session.get('dice_result')
    dice_won = session.get('dice_won')
    scene_data = SCENES[scene_id]
    return render_template('scene.html',
                           scene_id=scene_id,
                           scene=scene_data,
                           lives=lives,
                           dice_result=dice_result,
                           dice_won=dice_won)


@app.route('/action', methods=['POST'])
def action():
    btn = request.form.get('btn')
    scene_id = session.get('scene', 1)
    lives = session.get('lives', 3)

    # Dice roll scene (scene 11, c1 from scene 10 already moved us here)
    if scene_id == 11 and btn == 'next':
        dice = random.randint(1, 6)
        won = dice % 2 == 0
        session['dice_result'] = dice
        session['dice_won'] = won
        session['scene'] = 12 if won else 13
        return redirect(url_for('scene'))

    # Restart from death scenes
    if btn == 'restart':
        lives -= 1
        session['lives'] = lives
        session['dice_result'] = None
        session['dice_won'] = None
        if lives <= 0:
            session['scene'] = 0   # permanent death
        else:
            session['scene'] = 1
        return redirect(url_for('scene'))

    # Normal transitions
    next_scene = TRANSITIONS.get((scene_id, btn))
    if next_scene is not None:
        session['scene'] = next_scene
        session['dice_result'] = None
        session['dice_won'] = None
    return redirect(url_for('scene'))


@app.route('/restart')
def full_restart():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
