from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import UserProfile, Message, MessageLog, Certificate, UserRole
from .forms import UserRegistrationForm, UserLoginForm, SendMessageForm, CAApprovalForm


# ===================== HOME PAGE =====================
def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


# ===================== AUTHENTICATION VIEWS =====================
@require_http_methods(["GET", "POST"])
def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile with role
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data.get('role', UserRole.USER)
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {user.first_name or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ===================== DASHBOARD VIEW =====================
@login_required
def dashboard(request):
    """User dashboard based on role"""
    profile = request.user.profile
    context = {
        'user_role': profile.role,
        'role_display': profile.get_role_display(),
    }
    
    if profile.role == UserRole.CLOUD_AUTHORITY:
        # CA dashboard - messages waiting for certificate
        pending_messages = Message.objects.filter(status='ROUTER_ACCEPTED')
        context['pending_messages'] = pending_messages
        context['total_pending'] = pending_messages.count()
        return render(request, 'dashboard/ca_dashboard.html', context)
    
    elif profile.role == UserRole.ROUTER:
        # Router dashboard - messages waiting for acceptance
        pending_messages = Message.objects.filter(status='SENT')
        context['pending_messages'] = pending_messages
        context['total_pending'] = pending_messages.count()
        return render(request, 'dashboard/router_dashboard.html', context)
    
    elif profile.role == UserRole.PUBLISHER:
        # Publisher dashboard
        context['recent_messages'] = Message.objects.filter(sender=request.user)[:10]
        return render(request, 'dashboard/publisher_dashboard.html', context)
    
    else:  # Regular USER
        sent = Message.objects.filter(sender=request.user).count()
        received = Message.objects.filter(receiver=request.user).count()
        context['sent_count'] = sent
        context['received_count'] = received
        context['recent_received'] = Message.objects.filter(
            receiver=request.user
        ).order_by('-timestamp')[:5]
        return render(request, 'dashboard/user_dashboard.html', context)


# ===================== MESSAGE VIEWS =====================
@login_required
def send_message(request):
    """Send a new message"""
    if request.method == 'POST':
        form = SendMessageForm(request.POST, current_user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.encrypt_content(form.cleaned_data['content'])
            message.status = 'SENT'
            message.save()
            
            # Log the action
            MessageLog.objects.create(
                message=message,
                actor=request.user,
                log_type='SEND',
                notes='User sent message'
            )
            
            messages.success(request, 'Message sent successfully!')
            return redirect('inbox')
    else:
        form = SendMessageForm(current_user=request.user)
    
    return render(request, 'messages/send_message.html', {'form': form})


@login_required
def inbox(request):
    """User inbox - received messages"""
    messages_list = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messages/inbox.html', {'page_obj': page_obj})


@login_required
def outbox(request):
    """User outbox - sent messages"""
    messages_list = Message.objects.filter(sender=request.user).order_by('-timestamp')
    
    from django.core.paginator import Paginator
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messages/outbox.html', {'page_obj': page_obj})


@login_required
def view_message(request, message_id):
    """View a single message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check permission
    if request.user != message.sender and request.user != message.receiver:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('inbox')
    
    decrypted_content = message.decrypt_content()
    
    return render(request, 'messages/view_message.html', {
        'message': message,
        'content': decrypted_content,
    })


# ===================== ROUTER VIEWS =====================
@login_required
def router_accept_message(request, message_id):
    """Router accepts a message"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != UserRole.ROUTER:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard')
    
    message = get_object_or_404(Message, id=message_id, status='SENT')
    
    if request.method == 'POST':
        message.status = 'ROUTER_ACCEPTED'
        message.updated_at = timezone.now()
        message.save()
        
        MessageLog.objects.create(
            message=message,
            actor=request.user,
            log_type='ACCEPT',
            notes='Router accepted message'
        )
        
        messages.success(request, 'Message accepted and sent to Cloud Authority.')
        return redirect('dashboard')
    
    return render(request, 'router/accept_message.html', {'message': message})


# ===================== CLOUD AUTHORITY VIEWS =====================
@login_required
def ca_create_certificate(request, message_id):
    """Cloud Authority creates certificate for message"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != UserRole.CLOUD_AUTHORITY:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard')
    
    message = get_object_or_404(Message, id=message_id, status='ROUTER_ACCEPTED')
    
    if request.method == 'POST':
        form = CAApprovalForm(request.POST)
        if form.is_valid():
            # Create certificate
            valid_until = timezone.now() + timedelta(days=365)
            certificate = Certificate.objects.create(
                message=message,
                issued_by=request.user,
                certificate_data=form.cleaned_data['certificate_data'],
                valid_until=valid_until
            )
            
            message.status = 'CERTIFICATE_CREATED'
            message.certificate = certificate.certificate_data
            message.updated_at = timezone.now()
            message.save()
            
            MessageLog.objects.create(
                message=message,
                actor=request.user,
                log_type='CERTIFICATE',
                notes='Certificate created by Cloud Authority'
            )
            
            messages.success(request, 'Certificate created successfully!')
            return redirect('dashboard')
    else:
        form = CAApprovalForm()
    
    context = {
        'message': message,
        'decrypted_content': message.decrypt_content(),
        'form': form
    }
    return render(request, 'ca/create_certificate.html', context)


# ===================== API ENDPOINTS =====================
@login_required
def api_message_status(request, message_id):
    """Get message status via API"""
    message = get_object_or_404(Message, id=message_id)
    
    if request.user != message.sender and request.user != message.receiver:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({
        'id': message.id,
        'status': message.status,
        'status_display': message.get_status_display(),
        'timestamp': message.timestamp.isoformat(),
        'updated_at': message.updated_at.isoformat(),
    })


@login_required
def api_user_stats(request):
    """Get user statistics"""
    user = request.user
    return JsonResponse({
        'username': user.username,
        'role': user.profile.role,
        'sent_messages': Message.objects.filter(sender=user).count(),
        'received_messages': Message.objects.filter(receiver=user).count(),
        'pending_actions': Message.objects.filter(
            status__in=['SENT', 'ROUTER_ACCEPTED']
        ).count() if user.profile.role in [UserRole.ROUTER, UserRole.CLOUD_AUTHORITY] else 0,
    })




#========================= CA / CreateCertificate PAGE =======================================
def ca_create_cerificate(request):
    cur = mydb.cursor()
    cur.execute(" SELECT mid, message FROM message WHERE status='Router Accepted'")
    userMessage = cur.fetchall()
    cur.close()
    if userMessage:
        return render(request, 'ca_create_cerificate.html', {'userMessage': userMessage})
    else:
        userMessage=''
        return render(request, 'ca_create_cerificate.html', {'userMessage': userMessage})

def ca_cc_after(request):
    if request.method == 'POST' and 'fid' in request.POST and 'msg' in request.POST:
        mid = request.POST.get('fid')
        userMsg = request.POST.get('msg')
        key = Fernet.generate_key()
        fernet = Fernet(key)
        encrypted_message = fernet.encrypt(userMsg.encode('utf-8'))
        signature = fernet.extract_timestamp(encrypted_message)
        status = 'Certificate Created'
        cursor = mydb.cursor()
        cursor.execute('UPDATE message SET pkey=%s, message=%s, certificate=%s, status=%s WHERE mid=%s', (key, encrypted_message, signature, status, mid))
        mydb.commit()

        return redirect('/ca-create-cerificate') 
    else:
        msg=''
        return render(request, 'ca_create_cerificate.html', {'msg': msg})

#==================================================== ROUTER PAGE =============================================================================
def router_login(request):
    return render(request, "router_login.html")

#========================= R / ACCEPT MESSAGE ROUTE PAGE =======================================
def r_accept_message(request):
    cur = mydb.cursor()
    cur.execute(" SELECT mid, sender, receiver, message FROM message WHERE status='Send'")
    userMessage = cur.fetchall()
    cur.close()
    if userMessage:
        return render(request, 'r_accept_message.html', {'userMessage': userMessage})
    else:
        userMessage=''
        return render(request, 'r_accept_message.html', {'userMessage': userMessage})

def r_am_after(request):
    if request.method == 'POST' and 'fid' in request.POST and 'msg' in request.POST:
        mid = request.POST.get('fid')
        userMsg = request.POST.get('msg')
        cursor = mydb.cursor()
        cursor.execute("UPDATE message SET status='Router Accepted' WHERE mid=%s", (mid, ))
        mydb.commit()

        return redirect('/r-accept-message') 
    else:
        msg=''
        return render(request, 'r_accept_message.html', {'msg': msg})
    

#========================= R / CE PAGE =======================================
def r_ce(request):
    cur = mydb.cursor()
    cur.execute(" SELECT mid, sender, receiver, message FROM message WHERE status='Certificate Created'")
    userMessage = cur.fetchall()
    cur.close()
    if userMessage:
        return render(request, 'r_ce.html', {'userMessage': userMessage})
    else:
        userMessage=''
        return render(request, 'r_ce.html', {'userMessage': userMessage})

def r_ce_after(request):
    if request.method == 'POST' and 'fid' in request.POST:
        mid = request.POST.get('fid')
        cursor = mydb.cursor()
        cursor.execute("UPDATE message SET status='CE Accepted' WHERE mid=%s", (mid,))
        mydb.commit()

        return redirect('/r-ce') 
    else:
        msg=''
        return render(request, 'r_ce.html', {'msg': msg})

#========================= R / STATUS PAGE =======================================
def r_status(request):
    cur = mydb.cursor()
    cur.execute(" SELECT mid, sender, receiver, status FROM message")
    userMessage = cur.fetchall()
    cur.close()
    if userMessage:
        return render(request, 'r_status.html', {'userMessage': userMessage})
    else:
        userMessage=''
        return render(request, 'r_status.html', {'userMessage': userMessage})


#==================================================== PUBLISHER PAGE =========================================================================
def publisher_login(request):
    return render(request, "publisher_login.html")


#========================= P / SEND AUTHENTICATION KEYS or NODES PAGE =======================================
def p_sak(request):
    cur = mydb.cursor()
    cur.execute(" SELECT mid, receiver FROM message WHERE status='CE Accepted'")
    userMessage = cur.fetchall()
    cur.close()
    if userMessage:
        return render(request, 'p_sak.html', {'userMessage': userMessage})
    else:
        userMessage=''
        return render(request, 'p_sak.html', {'userMessage': userMessage})

def p_sak_after(request):
    if request.method == 'POST' and 'fid' in request.POST:
        mid = request.POST.get('fid')
        cursor = mydb.cursor()
        cursor.execute("UPDATE message SET status='Received' WHERE mid=%s", (mid,))
        mydb.commit()

        return redirect('/p-sak') 
    else:
        msg=''
        return render(request, 'p_sak.html', {'msg': msg})

#==================================================== USER PAGE =============================================================================
def user_login(request):
    msg = ''
    if request.method == 'POST' and 'email' in request.POST and 'password' in request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM userdetails WHERE email = %s AND password = %s AND status='Accepted'" , (email, password))
        account = cursor.fetchone()
        if account:
            global uid, Username, emailid
            uid = account[0]
            Username = account[1]
            emailid = account[2]
            
            return redirect('/user-sendmessage')
        else:
            msg2 = 'Incorrect username/password! Please login with correct credentials'
            return render(request, 'user_login.html', {'msg2': msg2})
    return render(request, 'user_login.html')

#============================ USER * SEND MESSAGE PAGE ==========================================================
def user_sendmessage(request):
    cursor = mydb.cursor()
    cursor.execute("SELECT email FROM userdetails WHERE email != %s ORDER BY email ASC", (emailid, ))
    remail_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return render(request, 'user_sendmessage.html', {'remail_list': remail_list})

# key = Fernet.generate_key()
# fernet = Fernet(key)

def user_sm_after(request):
    if request.method == 'POST':
        receivermail = request.POST.get('receivermail')
        message = request.POST.get('message')
        certificate = ""
        ce = ""
        router = "router@gmail.com"
        status = 'Send'
        cur = mydb.cursor()    
        cur.execute("INSERT INTO message(sid, sname, sender, receiver, router, message, certificate, ce, status) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s) ", (uid, Username, emailid, receivermail, router, message, certificate, ce, status))
        mydb.commit()
        cur.close()
        msg = 'Message Send uccessfully.'
        return render(request, "user_sendmessage.html", {'msg': msg})
    return render(request, "user_sendmessage.html")    

#============================ USER * INBOX PAGE ==========================================================
def user_inbox(request):
    cur = mydb.cursor()
    cur.execute("SELECT * FROM message WHERE receiver=%s AND status='Received'", (emailid,))
    userInbox = cur.fetchall()
    cur.close()
    if userInbox:
        return render(request, 'user_inbox.html', {'userInbox': userInbox})
    else:
        userInbox=''
        return render(request, 'user_inbox.html', {'userInbox': userInbox})  

#============================ USER * OUTBOX PAGE ==========================================================
def user_outbox(request):
    cur = mydb.cursor()
    cur.execute(" SELECT mid, sid, receiver, date, pkey, message FROM message WHERE sender=%s AND status='Received'", (emailid, ))
    userOutbox = cur.fetchall()
    cur.close()
    if userOutbox: 
        return render(request, 'user_outbox.html', {'userOutbox': userOutbox})
    else:
        userOutbox=''
        return render(request, 'user_outbox.html', {'userOutbox': userOutbox})  

#============================ USER * OUTBOX display PAGE ==========================================================
def user_outboxdisplay(request):
    if request.method == 'POST' and 'fid' in request.POST and 'pkey' in request.POST and 'message' in request.POST:
        f1 = request.POST.get('fid')
        pkey = request.POST.get('pkey')

        con=mydb.cursor()
        con.execute("SELECT message FROM message WHERE status='Received' AND mid=%s", (f1, )) 
        msgfile = con.fetchone()
        con.close()
        if msgfile:
            fernet = Fernet(pkey)
            messagedata = fernet.decrypt(msgfile[0].decode('utf-8'))

            return render(request, 'user_outboxdisplay.html', {'f1':f1, 'messagedata': messagedata})
        else:
            messagedata=''
            f1 = ''
            return render(request, 'user_outboxdisplay.html', {'f1':f1, 'messagedata': messagedata})  

#============================ USER - SHOW INBOX/OUTBOX messages PAGE ==========================================================
def user_showedmessage(request):
    if request.method == 'POST' and 'fid' in request.POST and 'senderid' in request.POST:
        f1 = request.POST.get('fid')
        sid1 = request.POST.get('senderid')
        pkeyinput = request.POST.get('pkeyinput')
        try:
            con=mydb.cursor()
            con.execute("SELECT message FROM message WHERE status='Received' AND mid=%s AND sid=%s ", (f1,sid1, )) 
            msgfile = con.fetchone()
            con.close()
            if msgfile:
                fernet = Fernet(pkeyinput)
                decrypted_message = fernet.decrypt(msgfile[0].decode('utf-8'))
                msg="Received Data"
                return render(request, 'user_showedmessage.html', {'decrypted_message':decrypted_message, 'msg':msg}) 
            else:
                msg = 'Message Not Found.'
                decrypted_message=''
                return render(request, 'user_showedmessage.html', {'decrypted_message':decrypted_message, 'msg':msg})
        except:
            msg = "Plz Enter Authentication Key/Node"
            decrypted_message=''
            return render(request, 'user_showedmessage.html', {'decrypted_message':decrypted_message, 'msg':msg})



#==================================================== REGISTER PAGE ==========================================================================
def register_user(request):
    msg = ''
    if request.method == 'POST' and 'name' in request.POST and 'email' in request.POST and 'password' in request.POST and 'dob' in request.POST and 'mobile' in request.POST:
        # Create variables for easy access
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        dob = request.POST['dob']
        mobile = request.POST['mobile']
        status = "Accepted"
        
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,10}$"
        pattern = re.compile(reg)
        cursor = mydb.cursor()
        # Check if account exists using MySQL)
        cursor.execute('SELECT * FROM userdetails WHERE email = %s', (email,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.search(pattern,password):
            msg = 'Password should contain atleast one number, one lower case character, one uppercase character,one special symbol and must be between 6 to 10 characters long'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into employee table
            query2 = 'INSERT INTO userdetails VALUES (NULL, %s, %s, %s, %s,%s, %s)'
            cursor.execute(query2, (username, email, password, dob, mobile, status))
            mydb.commit()
            msg = 'You have successfully registered! Please proceed for login!'
            return render(request, 'user_login.html', {'msg': msg})
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        return msg
    return render(request, "register_user.html", {'msg': msg})
