from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, current_app
from flask_login import current_user, login_required
from project import db
from project.models import Video, Plan, Subscription
from project.main.forms import VideoForm
import os
from werkzeug.utils import secure_filename
import razorpay
from datetime import datetime, timedelta
import random # Import random for dummy data

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

@main.route('/trending')
def trending():
    # For now, let's just return all videos as trending, or a subset
    # In a real application, you would have a logic to determine trending videos
    all_videos = Video.query.all()
    # Shuffle for a "trending" effect or pick top N based on some criteria
    random.shuffle(all_videos)
    trending_videos = all_videos[:9] # Displaying a subset for demonstration
    return render_template('trending.html', trending_videos=trending_videos)


@main.route('/upload_video', methods=['GET', 'POST'])
@login_required
def upload_video():
    form = VideoForm()
    if form.validate_on_submit():
        video_file = form.video_file.data
        filename = secure_filename(video_file.filename)
        
        upload_path = os.path.join(current_app.root_path, 'static', 'videos')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        video_path = os.path.join(upload_path, filename)
        video_file.save(video_path)
        
        video = Video(title=form.title.data, description=form.description.data, filename=filename)
        db.session.add(video)
        db.session.commit()
        flash('Your video has been uploaded!', 'success')
        return redirect(url_for('main.index'))
    return render_template('upload_video.html', title='Upload Video', form=form)

@main.route('/video/<int:video_id>')
def video(video_id):
    video = Video.query.get_or_404(video_id)
    if not current_user.is_authenticated:
        flash('You need to be logged in to watch videos.', 'info')
        return redirect(url_for('users.login'))
    if not current_user.is_subscribed:
        flash('You need to subscribe to watch videos.', 'info')
        return redirect(url_for('main.subscribe'))
    return render_template('video.html', title=video.title, video=video)

@main.route('/subscribe')
@login_required
def subscribe():
    plans = Plan.query.all()
    return render_template('subscribe.html', title='Subscribe', plans=plans)

@main.route('/pay/<int:plan_id>')
@login_required
def pay(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    data = {
        'amount': plan.price,
        'currency': 'INR',
        'receipt': 'order_rcptid_11'
    }
    order = client.order.create(data=data)
    return render_template('payment.html', title='Payment', order=order, plan=plan, key_id=current_app.config['RAZORPAY_KEY_ID'])

@main.route('/payment_verified')
@login_required
def payment_verified():
    razorpay_payment_id = request.args.get('razorpay_payment_id')
    razorpay_order_id = request.args.get('razorpay_order_id')
    razorpay_signature = request.args.get('razorpay_signature')
    plan_id = request.args.get('plan_id')
    
    client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
    
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)
        
        plan = Plan.query.get(plan_id)
        
        subscription = Subscription(
            user_id=current_user.id,
            plan_id=plan.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            razorpay_subscription_id=razorpay_order_id # Using order_id as subscription_id for simplicity
        )
        db.session.add(subscription)
        
        current_user.is_subscribed = True
        db.session.commit()
        
        flash('Payment successful! You are now subscribed.', 'success')
    except razorpay.errors.SignatureVerificationError as e:
        flash('Payment verification failed. Please contact support.', 'danger')
        
    return redirect(url_for('main.index'))
