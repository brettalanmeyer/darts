from darts import app
from flask import Response, request, render_template, redirect
from darts.entities import mark_style as markStyleModel
from darts import model
from sqlalchemy.sql.expression import func
from sqlalchemy import desc
from datetime import datetime
from darts.entities import mailer
import json
import uuid

@app.route("/mark-styles/")
def mark_styles_index():
	admin = False
	if request.remote_addr == "10.9.1.207":
		admin = True

	markStyles = model.Model().select(markStyleModel.MarkStyle).filter_by(confirmed = 1).order_by(desc("createdAt"))
	if not admin:
		markStyles = markStyles.filter_by(approved = 1)

	dates = {}
	for markStyle in markStyles:
		dates[markStyle.id] = "{:%b %d, %Y} ".format(markStyle.createdAt)

	return render_template("markstyles/index.html", markStyles = markStyles, dates = dates, admin = admin)

@app.route("/mark-styles/new/")
def mark_styles_new():
	markStyle = markStyleModel.MarkStyle("", "", "", "", "", "", "", "", "")
	return render_template("markstyles/form.html", markStyle = markStyle)

@app.route("/mark-styles/", methods = ["POST"])
def mark_styles_create():
	name = request.form["name"]
	email = request.form["email"]
	one = request.form["one"].replace('width="320" height="240"', 'viewBox="0 0 320 240"')
	two = request.form["two"].replace('width="320" height="240"', 'viewBox="0 0 320 240"')
	three = request.form["three"].replace('width="320" height="240"', 'viewBox="0 0 320 240"')

	token = uuid.uuid4()

	newMarkStyle = markStyleModel.MarkStyle(name, email, token, one, two, three, 0, 0, datetime.now())
	model.Model().create(newMarkStyle)

	html = "<p>You have submitted a new mark style.</p><p>Please click on the link below to confirm your submission.</p><p><a href=\"" + request.url_root + "mark-styles/" + str(newMarkStyle.id) + "/confirm/" + str(token) + "/" + "\">Confirm Mark Style Submission</a></p><p>Thank you.</p>"

	mailer.Mailer().send(
		"You have submitted a new mark style.",
		html,
		html,
		email
	)

	return redirect("/mark-styles/")

@app.route("/mark-styles/<int:id>/", methods = ["POST"])
def mark_styles_update(id):
	model.Model().update(markStyleModel.MarkStyle, id, { "confirmed": 0, "approved": 0 })

	name = request.form["name"]
	email = request.form["email"]
	one = request.form["one"].replace('width="320" height="240"', 'viewBox="0 0 320 240"')
	two = request.form["two"].replace('width="320" height="240"', 'viewBox="0 0 320 240"')
	three = request.form["three"].replace('width="320" height="240"', 'viewBox="0 0 320 240"')

	token = uuid.uuid4()

	newMarkStyle = markStyleModel.MarkStyle(name, email, token, one, two, three, 0, 0, datetime.now())
	model.Model().create(newMarkStyle)

	html = "<p>You have updated an existing mark style.</p><p>Please click on the link below to confirm your update.</p><p><a href=\"" + request.url_root + "mark-styles/" + str(newMarkStyle.id) + "/confirm/" + str(token) + "/" + "\">Confirm Mark Style Update</a></p><p>Thank you.</p>"

	mailer.Mailer().send(
		"You have updated an existing mark style.",
		html,
		html,
		email
	)

	return redirect("/mark-styles/")

@app.route("/mark-styles/<int:id>/edit/", methods = ["GET"])
def mark_styles_edit(id):
	markStyle = model.Model().selectById(markStyleModel.MarkStyle, id)

	svgs = json.dumps([
		markStyle.one,
		markStyle.two,
		markStyle.three
	])

	return render_template("markstyles/form.html", markStyle = markStyle, svgs = svgs)

@app.route("/mark-styles/<int:id>/confirm/<path:token>/", methods = ["GET"])
def mark_styles_confirm(id, token):

	markStyle = model.Model().select(markStyleModel.MarkStyle).filter_by(id = id, token = token, confirmed = 0, approved = 0).first()

	if markStyle == None:
		return redirect("/mark-styles/%d/invalid/%s/" % (id, token))

	else:
		model.Model().update(markStyleModel.MarkStyle, id, { "confirmed": 1 })

		html = "<p>A new mark style has been submitted by " + markStyle.name + " for your review.</p><p>It may be approved or rejected here: " + request.url_root + "mark-styles/.</p>"

		mailer.Mailer().send(
			"A new mark style has been submitted.",
			html,
			html,
			"brettmeyerxpx@gmail.com"
		)

		return redirect("/mark-styles/%d/confirmed/%s/" % (id, token))

@app.route("/mark-styles/<int:id>/confirmed/<path:token>/", methods = ["GET"])
def mark_styles_confirmed(id, token):
	return render_template("markstyles/confirmed.html")

@app.route("/mark-styles/<int:id>/invalid/<path:token>/", methods = ["GET"])
def mark_styles_invalid(id, token):
	return render_template("markstyles/invalid.html")

@app.route("/mark-styles/<int:id>/approve/", methods = ["POST"])
def mark_styles_approve(id):
	model.Model().update(markStyleModel.MarkStyle, id, { "approved": 1 })
	return redirect("/mark-styles/")

@app.route("/mark-styles/<int:id>/reject/", methods = ["POST"])
def mark_styles_reject(id):
	model.Model().update(markStyleModel.MarkStyle, id, { "approved": 0 })
	return redirect("/mark-styles/")

@app.route("/mark-styles/<int:id>/delete/", methods = ["POST"])
def mark_styles_delete(id):
	model.Model().delete(markStyleModel.MarkStyle, id)
	return redirect("/mark-styles/")

@app.route("/mark-styles/<int:id>/<path:num>.svg")
def mark_styles_svg(id, num):

	markStyle = model.Model().selectById(markStyleModel.MarkStyle, id)

	if num == "one":
		style = markStyle.one
	elif num == "two":
		style = markStyle.two
	else:
		style = markStyle.three

	return Response(style, mimetype = "image/svg+xml")

