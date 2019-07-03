from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify


from . models import User,Post,db
from . forms import  SignUpForm,SignInForm,AboutUserForm,AddPostForm
from blogger  import app

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signupform = SignUpForm(request.form)
    if request.method == 'POST':
        reg = User(signupform.firstname.data, signupform.lastname.data,signupform.username.data, signupform.password.data,signupform.email.data)
        db.session.add(reg)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('signup.html', signupform=signupform)


@app.route('/signin',methods=['GET','POST'])
def signin():
    signinform=SignInForm()
    if request.method=='POST':
        em=signinform.email.data
        log=User.query.filter_by(email=em).first()
        if log.password==signinform.password.data:
            current_user=log.username
            session['username']=current_user
            session['user_available']=True

            return redirect(url_for('show_posts'))
    return render_template('signin.html',signinform=signinform)

@app.route('/add', methods=['GET', 'POST'])
def addpost():
    if session['user_available']:
        blogpost = AddPostForm(request.form)
        us = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            bp = Post(blogpost.title.data, blogpost.description.data, us.uid)
            db.session.add(bp)
            db.session.commit()
            return redirect(url_for('show_posts'))
        return render_template('add.html', blogpost=blogpost,user=us)
    flash('User is not Authenticated')
    return redirect(url_for('index'))

@app.route('/delete/<int:pid>/<post_owner>',methods=['GET','POST'])
def delete_post(pid,post_owner):
    if session['username']==post_owner:
        me=Post.query.get(pid)
        db.session.delete(me)
        db.session.commit()
        return redirect(url_for('show_posts'))
    flash('You are not a valid user to Delete this Post')
    return redirect(url_for('show_posts'))

@app.route('/update/<int:pid>/<post_owner>',methods=['GET','POST'])
def update_post(pid,post_owner):
    if session['username']==post_owner:
        me=Post.query.get(pid)
        us = User.query.filter_by(username=session['username']).first()
        blogpost=AddPostForm(obj=me)
        if request.method=='POST':
            bpost=Post.query.get(pid)
            bpost.title=blogpost.title.data
            bpost.description=blogpost.description.data
            db.session.commit()
            return redirect(url_for('show_posts'))
        return render_template('update.html',post=me,blogpost=blogpost)
    flash('You are not a valid user to Edit this Post')
    return redirect(url_for('show_posts'))


@app.route('/post')
def show_posts():
    if session['user_available']:
        user=User.query.all()
        post=Post.query.all()
        return render_template('post.html',post=post,user=user)
    flash('User is not authenticated')
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def post(post_id):
    if session['user_available']:
        #user=User.query.filter_by(username=session['username']).first()
        user=User.query.all()
        post=Post.query.filter_by(pid=post_id).one()
        return render_template('specified_post.html',post=post,user=user)
    flash('User is not authenticated')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    session['user_available']=False
    return redirect(url_for('index'))

@app.route('/about_user')
def about_user():
    aboutuserform =AboutUserForm()
    if session['user_available']:
        user=User.query.filter_by(username=session['username']).first()
        return render_template('about_user.html',user=user,aboutuserform =aboutuserform )
    flash('User is not authenticated')
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run()
