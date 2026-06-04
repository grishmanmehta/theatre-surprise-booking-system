from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import random
import json
from models import db, User, Theatre, Screen, Booking, City

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'grishmanmehta@gmail.com'
app.config['MAIL_PASSWORD'] = 'hqfq oipl fvta uygs'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Movie recommendations by genre
MOVIE_RECOMMENDATIONS = {
    'action': [
        "🎬 **John Wick 4** - Keanu Reeves returns as the legendary assassin",
        "🎬 **Mission: Impossible 7** - Tom Cruise's death-defying stunts continue",
        "🎬 **The Batman** - Dark, gritty reboot with Robert Pattinson",
        "🎬 **Top Gun: Maverick** - High-flying aerial action sequel",
        "🎬 **Black Panther: Wakanda Forever** - Epic superhero action",
        "🎬 **Avatar: The Way of Water** - Stunning visual spectacle",
        "🎬 **Mad Max: Fury Road** - High-octane post-apocalyptic thriller"
    ],
    'comedy': [
        "🎬 **Superbad** - Classic teen comedy about friendship",
        "🎬 **The Hangover** - Wild Vegas bachelor party gone wrong",
        "🎬 **Bridesmaids** - Hilarious wedding preparation chaos",
        "🎬 **Step Brothers** - Will Ferrell and John C. Reilly as immature stepbrothers",
        "🎬 **21 Jump Street** - Undercover cops in high school",
        "🎬 **Game Night** - Competitive game night turns real",
        "🎬 **Booksmart** - Smart students' wild night before graduation"
    ],
    'romance': [
        "🎬 **The Notebook** - Timeless love story that tugs heartstrings",
        "🎬 **La La Land** - Musical romance about dreams and love",
        "🎬 **Pride and Prejudice** - Classic Jane Austen adaptation",
        "🎬 **Crazy Rich Asians** - Glamorous modern romance",
        "🎬 **Before Sunrise** - Beautiful conversation-driven romance",
        "🎬 **A Star is Born** - Musical romance with emotional depth",
        "🎬 **The Proposal** - Funny fake relationship turns real"
    ],
    'drama': [
        "🎬 **The Shawshank Redemption** - Hope and friendship in prison",
        "🎬 **Forrest Gump** - Life story of an extraordinary ordinary man",
        "🎬 **The Godfather** - Epic crime family saga",
        "🎬 **Schindler's List** - Powerful historical drama",
        "🎬 **Fight Club** - Mind-bending psychological drama",
        "🎬 **Parasite** - Award-winning social class commentary",
        "🎬 **The Social Network** - Creation of Facebook drama"
    ],
    'horror': [
        "🎬 **Get Out** - Social thriller with horror elements",
        "🎬 **A Quiet Place** - Surviving in a world where sound kills",
        "🎬 **The Conjuring** - Classic supernatural horror based on true events",
        "🎬 **Hereditary** - Disturbing family horror masterpiece",
        "🎬 **It** - Terrifying clown horror adaptation",
        "🎬 **The Babadook** - Psychological horror about grief",
        "🎬 **Sinister** - Found footage supernatural horror"
    ],
    'sci-fi': [
        "🎬 **Interstellar** - Space exploration and time dilation",
        "🎬 **The Matrix** - Reality-bending cyberpunk classic",
        "🎬 **Inception** - Dream within a dream heist",
        "🎬 **Blade Runner 2049** - Visually stunning neo-noir sci-fi",
        "🎬 **Arrival** - Intelligent alien contact story",
        "🎬 **Dune** - Epic space fantasy adaptation",
        "🎬 **Ex Machina** - AI and consciousness thriller"
    ],
    'fantasy': [
        "🎬 **The Lord of the Rings Trilogy** - Epic fantasy adventure",
        "🎬 **Harry Potter Series** - Magical school and destiny",
        "🎬 **Pan's Labyrinth** - Dark fantasy during Spanish Civil War",
        "🎬 **The Chronicles of Narnia** - Magical wardrobe adventures",
        "🎬 **Stardust** - Charming fairy tale romance",
        "🎬 **The Princess Bride** - Classic fairy tale adventure",
        "🎬 **Willow** - 80s fantasy classic about a destined child"
    ],
    'thriller': [
        "🎬 **Gone Girl** - Twisting marital thriller",
        "🎬 **Se7en** - Dark crime thriller about the seven deadly sins",
        "🎬 **The Silence of the Lambs** - Psychological thriller masterpiece",
        "🎬 **Prisoners** - Intense kidnapping mystery",
        "🎬 **Zodiac** - Investigative thriller about serial killer",
        "🎬 **Shutter Island** - Mind-bending psychological thriller",
        "🎬 **Nightcrawler** - Dark thriller about crime journalism"
    ],
    'animation': [
        "🎬 **Spider-Man: Into the Spider-Verse** - Revolutionary animation style",
        "🎬 **Toy Story Series** - Beloved toys come to life",
        "🎬 **Spirited Away** - Studio Ghibli masterpiece",
        "🎬 **The Lion King** - Animated classic about responsibility",
        "🎬 **Finding Nemo** - Underwater father-son adventure",
        "🎬 **Frozen** - Magical sisterly love story",
        "🎬 **Coco** - Beautiful Mexican Day of the Dead celebration"
    ],
    'adventure': [
        "🎬 **Indiana Jones Series** - Classic archaeological adventures",
        "🎬 **Jurassic Park** - Dinosaurs come back to life",
        "🎬 **Pirates of the Caribbean** - Swashbuckling pirate adventures",
        "🎬 **The Goonies** - Kids' treasure hunt adventure",
        "🎬 **Jumanji: Welcome to the Jungle** - Video game comes to life",
        "🎬 **The Mummy** - Ancient Egyptian adventure",
        "🎬 **National Treasure** - Historical treasure hunt"
    ]
}

# Chatbot responses
CHATBOT_RESPONSES = {
    'greeting': [
        "Hello! I'm your theatre booking assistant. I can help you with booking, pricing, theatre locations, customization options, and movie recommendations! 😊",
        "Hi there! Ready to create a magical surprise? I can guide you through booking, explain pricing, help with customization, and suggest great movies! 🎭",
        "Welcome! I'm here to help you plan the perfect surprise. Ask me about booking, theatres, pricing, customization, or movie recommendations! ✨"
    ],
    'booking_process': [
        "Here's how to book: 1) Go to 'Book Now' → 2) Select your city → 3) Choose a theatre → 4) Pick a screen → 5) Select date/time → 6) Choose occasion → 7) Add movie preference → 8) Customize your surprise! 🎬",
        "Booking is simple: Start from the homepage, click 'Book Now', choose your city, theatre, screen, then pick date/time, occasion, movie preference, and add customizations! 📅",
        "To book: Navigate to booking page → Select city → Choose theatre → Pick screen → Select date & time → Choose occasion → Add movie preference → Personalize with surprises! 🎉"
    ],
    'theatres_locations': [
        "We have premium theatres in: **Mumbai** - Ajanta Cinema, Anand Cinemas, G7 Multiplex, Sterling Cineplex | **Pune** - City Pride Royal Cinemas, Rahul Cinema | **Delhi** - Batra Reels Cinemas, M2K Pitampura, M2K Rohini, Wave Cinemas 🏙️",
        "Our theatre locations: **Mumbai**: 4 theatres including Ajanta Cinema & G7 Multiplex | **Pune**: 2 theatres including City Pride | **Delhi**: 4 theatres including Wave Cinemas & M2K. All with multiple screens! 🎦",
        "We serve 3 cities: **Mumbai** (4 theatres), **Pune** (2 theatres), **Delhi** (4 theatres). Each theatre has 3 screens with modern facilities for your perfect surprise! 🌆"
    ],
    'pricing_details': [
        "**Pricing Breakdown:** Base booking fee: ₹5000 | Cake: +₹500 | Balloons: +₹300 | Decoration: +₹1000 | Party Poppers: +₹200 | Flowers: +₹800 | Chocolate Bouquet: +₹600. Total depends on your customization! 💰",
        "**Cost Details:** Starting at ₹5000 for basic booking. Add-ons: Cake ₹500, Balloons ₹300, Full Decoration ₹1000, Party Poppers ₹200, Flowers ₹800, Chocolate Bouquet ₹600. Mix and match as you like! 💵",
        "**Price Structure:** Base: ₹5000. Customization: Cake ₹500, Balloons ₹300, Decoration ₹1000, Party Poppers ₹200, Flowers ₹800, Chocolate Bouquet ₹600. You only pay for what you choose! 🎂"
    ],
    'customization_options': [
        "**Customization Options:** 🎂 Cake | 🎈 Balloons | ✨ Full Decoration | 🎉 Party Poppers | 💐 Flowers | 🍫 Chocolate Bouquet. You can also upload personal media (photos/videos) and add a special message! 🎁",
        "**Personalize Your Surprise:** Add cakes, balloons, decorations, party poppers, flowers, or chocolate bouquets. Plus, upload your photos/videos and write a heartfelt message for the big screen! 💝",
        "**Make It Unique:** Choose from cakes, balloons, decorations, party poppers, flowers, and chocolate bouquets. Don't forget to upload media files and add your personal message for a truly special experience! 🎊"
    ],
    'occasion_ideas': [
        "**Perfect For:** 🎂 Birthdays | 💑 Anniversaries | 💍 Proposals | 💕 Valentine's Day | 🎓 Graduations | 🏆 Achievements | 💖 Just Because! Any special moment deserves a grand surprise! 🌟",
        "**Celebrate:** Birthdays, Anniversaries, Proposals, Valentine's Day, or any special occasion! We've helped create magical moments for all types of celebrations! 🎂",
        "**Occasion Ideas:** Birthday surprises, anniversary celebrations, romantic proposals, Valentine's Day specials, graduation parties, or simply to show someone you care! 💕"
    ],
    'time_slots': [
        "**Available Time Slots:** 11:00 AM, 1:00 PM, 3:00 PM, 5:00 PM, 7:00 PM, 8:00 PM. Each slot is 2 hours long. Book in advance to secure your preferred time! ⏰",
        "**Session Times:** We offer 2-hour sessions at 11AM, 1PM, 3PM, 5PM, 7PM, and 8PM. Choose what works best for your surprise celebration! 🕐",
        "**Booking Slots:** Available at 11:00, 13:00, 15:00, 17:00, 19:00, and 20:00. Each session lasts 2 hours for a complete surprise experience! 📅"
    ],
    'media_upload': [
        "**Media Upload:** You can upload photos, videos, or collages (max 16MB) to be displayed on the big screen during your surprise! Supported formats: images (PNG, JPG, GIF) and videos (MP4, MOV, AVI) 📸",
        "**Personal Media:** Upload your photos or videos (under 16MB) to make the surprise more personal. They'll be displayed on screen during the celebration! 🎬",
        "**Add Your Media:** Share photos/videos (max 16MB) that will play on the big screen. Perfect for memories, messages, or creating a personalized slideshow! 💫"
    ],
    'help_support': [
        "I can help with: Booking process, Pricing details, Theatre locations, Customization options, Occasion ideas, Time slots, Media uploads, Movie recommendations, and any other questions! 🤝",
        "Need assistance? I can explain: How to book, Cost breakdown, Available theatres, Customization choices, Perfect occasions, Time availability, Movie suggestions, or anything else! 💫",
        "How can I assist? I can guide you through booking, explain pricing, show theatre options, suggest customizations, recommend occasions, suggest movies, and answer all your questions! ❓"
    ],
    'default': [
        "I'm here to help with theatre bookings and movie recommendations! Try asking about: booking process, pricing, theatre locations, customization options, occasion ideas, or movie suggestions. What would you like to know? 🎭",
        "I'd love to help you plan the perfect surprise! Ask me about: how to book, costs involved, available theatres, customization choices, suitable occasions, or movie recommendations. What's on your mind? 💡",
        "Let me help you create a magical moment! I can assist with: booking steps, pricing details, theatre info, personalization options, occasion planning, or movie suggestions. What would you like to know? ✨"
    ]
}


def get_chatbot_response(message):
    message_lower = message.lower()

    # Movie recommendation detection
    if any(word in message_lower for word in
           ['movie recommendation', 'suggest movie', 'movie suggest', 'recommend movie', 'what movie', 'good movie',
            'movies to watch']):
        # Check for specific genre requests
        for genre, movies in MOVIE_RECOMMENDATIONS.items():
            if genre in message_lower:
                response = f"🎬 **Great {genre.title()} Movies:**\n\n"
                for i, movie in enumerate(movies[:5], 1):
                    response += f"{movie}\n"
                response += f"\nWant more {genre} recommendations or suggestions for another genre?"
                return response

        # General movie recommendation
        response = "🎬 **I can recommend movies by genre!** Try asking for:\n\n"
        response += "• Action movies 🎯\n"
        response += "• Comedy films 😄\n"
        response += "• Romance movies 💕\n"
        response += "• Drama films 🎭\n"
        response += "• Horror movies 👻\n"
        response += "• Sci-Fi films 🚀\n"
        response += "• Fantasy movies 🧙‍♂️\n"
        response += "• Thriller films 🔍\n"
        response += "• Animation movies 🐭\n"
        response += "• Adventure films 🗺️\n\n"
        response += "Just tell me what genre you're interested in! 🎦"
        return response

    # Specific genre requests
    for genre in MOVIE_RECOMMENDATIONS.keys():
        if f'{genre} movie' in message_lower or f'{genre} film' in message_lower:
            response = f"🎬 **Top {genre.title()} Movies:**\n\n"
            for i, movie in enumerate(MOVIE_RECOMMENDATIONS[genre][:5], 1):
                response += f"{movie}\n"
            response += f"\nThese are some amazing {genre} films! Want more recommendations?"
            return response

    # Greeting detection
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']):
        return random.choice(CHATBOT_RESPONSES['greeting'])

    # Booking process
    elif any(word in message_lower for word in
             ['how to book', 'booking process', 'how do i book', 'steps to book', 'booking steps', 'reserve',
              'make booking']):
        return random.choice(CHATBOT_RESPONSES['booking_process'])

    # Theatres and locations
    elif any(word in message_lower for word in
             ['theatre', 'cinema', 'location', 'city', 'mumbai', 'pune', 'delhi', 'where', 'locations', 'venues']):
        return random.choice(CHATBOT_RESPONSES['theatres_locations'])

    # Pricing
    elif any(word in message_lower for word in
             ['price', 'cost', 'money', 'fee', 'how much', 'pricing', 'charges', 'rate', 'rates']):
        return random.choice(CHATBOT_RESPONSES['pricing_details'])

    # Customization
    elif any(word in message_lower for word in
             ['custom', 'decorate', 'decoration', 'cake', 'balloon', 'personalize', 'customization', 'addons',
              'extras']):
        return random.choice(CHATBOT_RESPONSES['customization_options'])

    # Occasions
    elif any(word in message_lower for word in
             ['occasion', 'birthday', 'anniversary', 'proposal', 'valentine', 'celebration', 'event', 'surprise']):
        return random.choice(CHATBOT_RESPONSES['occasion_ideas'])

    # Time slots
    elif any(word in message_lower for word in
             ['time', 'slot', 'schedule', 'availability', 'when', 'timing', 'session', 'duration']):
        return random.choice(CHATBOT_RESPONSES['time_slots'])

    # Media upload
    elif any(word in message_lower for word in ['photo', 'video', 'media', 'upload', 'picture', 'image', 'file']):
        return random.choice(CHATBOT_RESPONSES['media_upload'])

    # Help
    elif any(word in message_lower for word in ['help', 'support', 'assist', 'guide', 'what can you do', 'help me']):
        return random.choice(CHATBOT_RESPONSES['help_support'])

    # Specific questions with detailed answers
    elif 'how much' in message_lower and ('cake' in message_lower or 'balloon' in message_lower):
        return "Cake costs ₹500 and balloons cost ₹300. You can add both or choose individual items based on your preference! 🎂🎈"

    elif 'decorate' in message_lower or 'decoration' in message_lower:
        return "Full decoration setup costs ₹1000 and includes thematic decor to match your occasion. You can also add balloons (₹300) separately! ✨"

    elif 'flower' in message_lower or 'bouquet' in message_lower:
        return "Fresh flowers cost ₹800 and chocolate bouquets cost ₹600. Both make wonderful additions to any surprise celebration! 💐🍫"

    elif 'screen' in message_lower:
        return "Each theatre has 3 screens with capacities of 50 people. All screens are equipped with modern projection and sound systems for the best experience! 🎦"

    elif 'capacity' in message_lower or 'people' in message_lower or 'guests' in message_lower:
        return "Each screen can accommodate up to 50 people, perfect for intimate surprise celebrations with close friends and family! 👨‍👩‍👧‍👦"

    elif 'duration' in message_lower or 'how long' in message_lower:
        return "Each booking slot is 2 hours long, giving you plenty of time for the surprise, celebrations, and creating beautiful memories! ⏱️"

    elif 'available' in message_lower and 'time' in message_lower:
        return "We have 6 time slots daily: 11AM, 1PM, 3PM, 5PM, 7PM, and 8PM. Each is a 2-hour session for your complete surprise experience! 🕐"

    elif 'city' in message_lower:
        return "We currently serve Mumbai, Pune, and Delhi with multiple premium theatres in each city. Which city are you interested in? 🏙️"

    elif 'mumbai' in message_lower:
        return "In Mumbai, we have: Ajanta Cinema (Borivali), Anand Cinemas (Thane), G7 Multiplex (Bandra), Sterling Cineplex (Fort). All with excellent facilities! 🌃"

    elif 'pune' in message_lower:
        return "In Pune, we have: City Pride Royal Cinemas (Pimpri) and Rahul Cinema (Shivajinagar). Both offer great screens for your surprise! 🏞️"

    elif 'delhi' in message_lower:
        return "In Delhi, we have: Batra Reels Cinemas (Friends Colony), M2K Pitampura, M2K Rohini, and Wave Cinemas (Raja Garden). Multiple locations to choose from! 🏛️"

    elif 'what is' in message_lower and 'theatre' in message_lower:
        return "TheatreMagic lets you book cinema screens for private surprises! Display personal messages, photos, videos on the big screen for birthdays, proposals, anniversaries and more! 🎭"

    elif 'work' in message_lower and 'how' in message_lower:
        return "Here's how it works: You book a screen, we help you surprise your loved one with their photos/messages on the big screen, plus optional decorations and gifts! ✨"

    else:
        return random.choice(CHATBOT_RESPONSES['default'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chatbot/send', methods=['POST'])
def chatbot_send():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        bot_response = get_chatbot_response(user_message)

        return jsonify({
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.now().strftime('%H:%M')
        })

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password, name=name)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/cities')
def cities():
    cities = City.query.all()
    return render_template('cities.html', cities=cities)


@app.route('/theatres/<int:city_id>')
def theatres(city_id):
    city = City.query.get_or_404(city_id)
    theatres = Theatre.query.filter_by(city_id=city_id).all()
    return render_template('theatres.html', city=city, theatres=theatres)


@app.route('/screens/<int:theatre_id>')
def screens(theatre_id):
    theatre = Theatre.query.get_or_404(theatre_id)
    screens = Screen.query.filter_by(theatre_id=theatre_id).all()
    return render_template('screens.html', theatre=theatre, screens=screens)


@app.route('/booking/<int:screen_id>', methods=['GET', 'POST'])
@login_required
def booking(screen_id):
    screen = Screen.query.get_or_404(screen_id)

    if request.method == 'POST':
        # Check for conflicting bookings
        booking_date = request.form['booking_date']
        booking_time = request.form['booking_time']

        existing_booking = Booking.query.filter_by(
            screen_id=screen_id,
            booking_date=booking_date,
            booking_time=booking_time
        ).first()

        if existing_booking:
            flash('This time slot is already booked! Please choose another.', 'danger')
            return redirect(url_for('booking', screen_id=screen_id))

        # Handle file upload
        media_file = None
        if 'media_file' in request.files:
            file = request.files['media_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                media_file = filename

        # Create booking
        booking = Booking(
            user_id=current_user.id,
            screen_id=screen_id,
            booking_date=booking_date,
            booking_time=booking_time,
            occasion=request.form['occasion'],
            movie_preference=request.form.get('movie_preference', ''),
            message=request.form.get('message', ''),
            media_file=media_file,
            cake=bool(request.form.get('cake')),
            balloons=bool(request.form.get('balloons')),
            decoration=bool(request.form.get('decoration')),
            party_poppers=bool(request.form.get('party_poppers')),
            flowers=bool(request.form.get('flowers')),
            chocolate_bouquet=bool(request.form.get('chocolate_bouquet'))
        )

        db.session.add(booking)
        db.session.commit()

        # Send confirmation email
        send_confirmation_email(booking)

        flash('Booking confirmed! Check your email for confirmation.', 'success')
        return redirect(url_for('confirmation', booking_id=booking.id))

    return render_template('booking.html', screen=screen)


def send_confirmation_email(booking):
    try:
        msg = Message('Theatre Booking Confirmation',
                      recipients=[booking.user.email])
        msg.body = f"""
        Dear {booking.user.name},

        Your theatre booking has been confirmed!

        Booking Details:
        Theatre: {booking.screen.theatre.name}
        Screen: {booking.screen.name}
        Date: {booking.booking_date}
        Time: {booking.booking_time}
        Occasion: {booking.occasion}
        Movie Preference: {booking.movie_preference if booking.movie_preference else 'Not specified'}

        Total Amount: ₹{calculate_total(booking)}

        Thank you for choosing our service!
        """
        mail.send(msg)
    except Exception as e:
        print(f"Email sending failed: {e}")


def calculate_total(booking):
    base_price = 5000  # Base price
    additions = 0

    if booking.cake: additions += 500
    if booking.balloons: additions += 300
    if booking.decoration: additions += 1000
    if booking.party_poppers: additions += 200
    if booking.flowers: additions += 800
    if booking.chocolate_bouquet: additions += 600

    return base_price + additions


@app.route('/confirmation/<int:booking_id>')
@login_required
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))

    return render_template('confirmation.html', booking=booking, total=calculate_total(booking))


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))

    bookings = Booking.query.all()
    return render_template('admin.html', bookings=bookings)


@app.route('/api/available_slots/<int:screen_id>')
def available_slots(screen_id):
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date required'}), 400

    try:
        screen = Screen.query.get_or_404(screen_id)

        # Get all booked slots for this screen and date
        bookings = Booking.query.filter_by(screen_id=screen_id, booking_date=date).all()
        booked_times = [booking.booking_time for booking in bookings]

        # Get all available slots for this screen
        if screen.available_slots:
            all_slots = [slot.strip() for slot in screen.available_slots.split(',')]
        else:
            # Default slots if none specified
            all_slots = ["11:00", "13:00", "15:00", "17:00", "19:00", "20:00"]

        # Filter out booked slots
        available_slots = [slot for slot in all_slots if slot not in booked_times]

        return jsonify({
            'available_slots': available_slots,
            'total_slots': len(all_slots),
            'booked_slots': len(booked_times)
        })

    except Exception as e:
        print(f"Error in available_slots: {e}")
        return jsonify({'error': 'Internal server error'}), 500


def init_db():
    with app.app_context():
        db.create_all()

        # Add initial data
        if not City.query.first():
            # Cities
            mumbai = City(name='Mumbai')
            pune = City(name='Pune')
            delhi = City(name='Delhi')

            db.session.add_all([mumbai, pune, delhi])
            db.session.commit()

            # Theatres for Mumbai
            theatres_mumbai = [
                Theatre(name='Ajanta Cinema', address='Ajanta Square Mall, Borivali West', city_id=mumbai.id),
                Theatre(name='Anand Cinemas', address='Thane East', city_id=mumbai.id),
                Theatre(name='G7 Multiplex', address='Bandra West', city_id=mumbai.id),
                Theatre(name='Sterling Cineplex', address='Fort Mumbai', city_id=mumbai.id)
            ]

            # Theatres for Pune
            theatres_pune = [
                Theatre(name='City Pride Royal Cinemas', address='Pimpri', city_id=pune.id),
                Theatre(name='Rahul Cinema', address='Shivajinagar', city_id=pune.id)
            ]

            # Theatres for Delhi
            theatres_delhi = [
                Theatre(name='Batra Reels Cinemas', address='Friends Colony West, New Delhi', city_id=delhi.id),
                Theatre(name='M2K Pitampura', address='Pitampura, New Delhi', city_id=delhi.id),
                Theatre(name='M2K Rohini', address='Sector 3, New Delhi', city_id=delhi.id),
                Theatre(name='Wave Cinemas', address='Raja Garden, New Delhi', city_id=delhi.id)
            ]

            db.session.add_all(theatres_mumbai + theatres_pune + theatres_delhi)
            db.session.commit()

            # Add screens for each theatre with time slots
            for theatre in Theatre.query.all():
                for i in range(1, 4):  # 3 screens per theatre
                    # Different time slots for different screens
                    if i == 1:
                        slots = "11:00,13:00,15:00,17:00,19:00,20:00"
                    elif i == 2:
                        slots = "11:00,13:00,15:00,17:00,19:00,20:00"
                    else:
                        slots = "11:00,13:00,15:00,17:00,19:00,20:00"

                    screen = Screen(
                        name=f'Screen {i}',
                        capacity=50,
                        theatre_id=theatre.id,
                        available_slots=slots
                    )
                    db.session.add(screen)

            # Create admin user
            admin_user = User(
                email='admin@theatre.com',
                password=generate_password_hash('admin123'),
                name='Admin',
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    init_db()
    app.run(debug=True)