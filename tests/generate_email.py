import random
import mailbox
from time import mktime
from email.utils import formatdate
from email.message import EmailMessage
from email.utils import formatdate
from datetime import datetime, timedelta

EMAIL_BODIES = [
    "Just wanted to check in and see how you're doing. Let's catch up soon!",
    "Remember our meeting next week. Don't forget to bring the documents.",
    "There's a sale going on at your favorite store! Don't miss out!",
    "I saw this article and thought of you. Hope you find it interesting!",
    "Happy Birthday! Wishing you a fantastic day filled with joy and laughter.",
    "Your package has been shipped and should arrive within 3-5 business days.",
    "We've updated our privacy policy. Please take a moment to review the changes.",
    "Congratulations on your work anniversary! Here's to many more years of success.",
    "Friendly reminder: Your subscription is about to renew. No action is needed.",
    "Looking forward to our dinner plans. Shall we say 7 pm at the usual spot?",
    "Your flight details have been updated. Please check your itinerary for the new times.",
    "Your monthly statement is available. Please log in to your account to view the details.",
    "We miss you! Come back and visit us soon for a special returning customer discount.",
    "Thank you for your recent purchase. We'd love to hear your feedback.",
    "It's time for your regular check-up. Please call our office to schedule an appointment."
]

NEXT_STEP_EMAIL_BODIES = [
    'Hi applicant, We are impressed with your background and would like to invite you to participate in Google\'s Online Coding Challenge. This is the first step in our interview process for the Software Engineering position. The challenge will take place on our secure online platform and is designed to assess your coding skills and problem-solving abilities. Please select a time slot that best fits your schedule within the next week: example.com/link We\'re looking forward to seeing your innovative solutions!  Best, The Google Recruitment Team',
    'Dear applicant, We are excited to extend an invitation to you for Amazon\'s Software Development Engineer online assessment. This assessment is a great opportunity for you to showcase your technical expertise and for us to get to know you better.  You can access the assessment via the following link, which will be active for the next 72 hours: example.com/link If you have any questions or need to reschedule, please don\'t hesitate to reach out.  Best regards, Amazon University Recruiting',
    'Hello applicant, As part of our search for talented individuals, Meta is inviting you to take part in our Engineering Code Assessment. This is a chance for you to demonstrate your coding prowess and for us to identify potential matches for our engineering team. Please complete the assessment at your earliest convenience, but no later than two weeks from today: example.com/link Should you encounter any issues or require assistance, we\'re here to help. Warm regards, The Meta Recruiting Team.',
    'Dear applicant, You are cordially invited to participate in Apple\'s exclusive Online Assessment Day for the Software Engineer role. This is an excellent opportunity for you to engage in a variety of coding challenges and demonstrate your creativity. To confirm your participation, please RSVP by selecting a suitable date here: example.com/link. We are eager to witness your approach to solving real-world problems.  Kind regards, Apple Talent Acquisition.',
    'Greetings applicant, We are pleased to invite you to Microsoft\'s online assessment for the Software Engineer role. This assessment is designed to understand your technical skills in a structured, problem-solving environment. To begin the assessment, please follow this link, which will be active for the next five days: example.com/lin. We appreciate your interest in joining Microsoft and look forward to your participation. Best wishes, The Microsoft Careers Team'
    'Dear applicant, I hope this email finds you well. We have been very impressed with your background and the enthusiasm you have shown throughout the interview process. It is with great pleasure that we extend an invitation to you for an onsite interview for the Software Engineer position at Google. We believe that your skills and experiences align well with the requirements of our team, and we are excited about the possibility of you joining us. The interview will be an opportunity for you to learn more about our projects, culture, and the impact your work could have at Google. Please let us know your availability so we can arrange for your visit to our campus. We will provide detailed information about the schedule, travel arrangements, and any other necessary details upon confirmation. We look forward to the possibility of welcoming you to our team. Warm regards, Google Recruitment Team',
    'Hello applicant, We are delighted to inform you that after careful consideration of your application and preliminary interviews, you have been selected for an onsite interview for the Software Engineer role at Amazon. This is a significant step in our hiring process, and we are eager to have a more in-depth discussion with you about your technical abilities and how you could contribute to our team\'s success. Please reply to this email with a date that suits you best for the interview. Our recruitment team will then assist you with the necessary travel arrangements and provide you with a detailed agenda for the day. We are looking forward to meeting you in person and exploring the potential for a mutually rewarding collaboration.',
    'Hi applicant, Congratulations! You have successfully advanced to the next stage in the application process for the Software Engineer position at Meta. We are pleased to invite you to our headquarters for an onsite interview. During your visit, you will meet with several members of our engineering team and participate in a series of interviews designed to assess your problem-solving skills, technical expertise, and cultural fit. Could you please confirm your availability for the onsite interview? Our team will then reach out to finalize the details and assist you in planning your trip. We are thrilled at the prospect of having you join our innovative community and look forward to your response. Best wishes, Meta Careers Team',
    'Dear applicant, It is with great enthusiasm that we invite you to join us at Apple Park for an onsite interview for the Software Engineer position. Your profile stands out as a potential fit for our dynamic team, and we are keen to delve deeper into your experience and technical acumen. We will be scheduling interviews over the next few weeks and would like to know your preferred dates for visiting us. Upon receiving your response, we will arrange all the necessary details for your visit, including travel and accommodation if required. This interview will be a chance for you to engage with our engineers, experience our culture firsthand, and see the environment where you could be making a difference. Looking forward to your prompt reply and the opportunity to welcome you onsite. Kind regards, Apple Recruiting\' Best regards, Amazon Recruitment Team',
    'Hello applicant, We are excited to move forward with your application for the Software Engineer role at Microsoft. Your qualifications and interests appear to be a match for our needs, and we would like to invite you for an onsite interview at our campus. This will be an excellent opportunity for you to interact with our team, learn more about our projects, and discuss how your background can contribute to Microsoft\'s mission. Please let us know your availability so we can coordinate the details of your visit, including travel and accommodation if necessary. We look forward to the possibility of you joining our team and hope to hear from you soon. Sincerely, Microsoft Careers Team'
    ]

OFFER_EMAIL_BODIES = [
    'Dear applicant, We are thrilled to extend this official offer of employment for the position of Software Engineer at Google. Your technical skills, innovative thinking, and passion for problem-solving have impressed us throughout the interview process. We believe that your unique talents will be a valuable addition to our team as we continue to push the boundaries of technology. Enclosed with this email is your offer package detailing the terms of employment, including your compensation, benefits, and the many perks of being a Googler. Please review the offer at your earliest convenience and feel free to reach out with any questions. We hope to receive your acceptance and welcome you to our community of thinkers and innovators. Warmest congratulations, Google Talent Acquisition',
    'Hello applicant, Congratulations! After a thorough selection process, we are pleased to present you with an offer for the Software Engineer role at Amazon. Your experience and expertise are the perfect match for our ambitious team. In the attached document, you will find the details of your offer, including salary, benefits, and stock options. At Amazon, we are committed to fostering a culture of innovation and customer obsession, and we are excited about the prospect of you contributing to our ongoing success. Please take your time to review the offer and let us know if you have any questions. We are looking forward to your positive response and to you becoming an integral part of our Amazon family. Best regards, Amazon Recruitment Team',
    'Hi applicant, It gives us immense pleasure to offer you the position of Software Engineer at Meta. Your creativity and technical prowess stood out to us, and we are eager to see the impact you will make in creating world-class products that connect people around the globe. Your offer letter, which includes the full details of your compensation and benefits package, is attached to this email. We believe that your skills will greatly enhance our efforts to build a more connected world. We hope you are as excited as we are about this offer. Please review the attached document and let us know if you have any questions or need further information. Congratulations, and welcome to the team! Warm regards, Meta People Operations',
    'Dear applicant, Apple is proud to offer you the position of Software Engineer. Throughout our conversations, we\'ve been impressed with your technical expertise and the depth of your innovative spirit, which aligns perfectly with our mission to design products that enrich people’s lives. Enclosed is your offer package, which outlines your compensation, benefits, and the unique perks available to our team members. We trust that you will find Apple to be a place where you can continue to grow and be challenged. We look forward to you joining our team and contributing to the incredible work we do at Apple. Please review the offer and feel free to reach out with any questions. Congratulations, and we hope to hear from you soon. Sincerely, Apple Employment Relations',
    'Hello applicant, Congratulations on receiving an offer for the Software Engineer position at Microsoft! We are inspired by your vision and impressed with your technical skills. We are confident that you will bring valuable contributions to our team. Attached to this email, you will find the detailed offer letter, which includes your salary, comprehensive benefits, and additional perks of being part of the Microsoft family. We are committed to supporting our employees\' growth and innovation, and we look forward to you being a part of it. Please review the offer at your convenience and reach out with any questions or to discuss the next steps. We are hopeful that you will accept and become a part of our mission to empower every person and every organization on the planet to achieve more. With warm regards, Microsoft Talent Acquisition',
    ]

REJECTED_EMAIL_BODIES = [
    'Dear applicant, Thank you for investing the time to interview with us for the Software Engineer position at Google. We truly appreciate your interest in joining our team and the effort you put into the process. After careful consideration, we wanted to let you know that we will not be moving forward with your application. This decision was not easy and reflects the highly competitive nature of our selection process rather than a shortfall in your qualifications. We encourage you to apply for future roles that match your skills and experience. We also recommend keeping an eye on our careers page for new opportunities that are frequently posted. We wish you all the best in your career endeavors and are confident that you will find a role that is a perfect fit for your talents.  Kind regards, Google Careers Team',
    'Hello applicant, We appreciate the time and effort you dedicated to your interviews for the Software Engineer role at Amazon. It is with regret that we inform you that we have decided not to extend an offer at this time. Your skills and background are impressive, and this decision was difficult for us to make. It is a reflection of the specific requirements of the role and not of your professional qualities. Amazon is constantly growing and evolving, and we would welcome the opportunity to consider your application for future openings that better align with your expertise. Thank you for considering a career at Amazon, and we hope you will keep us in mind as you continue your job search.  Best wishes, Amazon Hiring Team',
    'Hi applicant, Thank you for your interest in the Software Engineer position with Meta and for the time you dedicated to the interview process. We are grateful for the chance to learn about your skills and experiences. After a comprehensive review, we have concluded that we will not be moving forward with your candidacy for this position. This was a challenging decision due to the high caliber of applicants like yourself. We are continually impressed by the passion and talent of our candidates and would encourage you to apply for future positions that you feel passionate about at Meta. We wish you success as you continue your career journey and hope you find a position that is the right fit for your skills and aspirations. Sincerely, Meta Recruiting',
    'Dear applicant, We wanted to reach out to you regarding your application for the Software Engineer position at Apple. After a thorough review, we have decided to move forward with other candidates who we feel more closely match the current needs of our team. This decision does not diminish the strong impression your background and interview left on us. We encourage you to continue to look at our job board and apply for future roles that align with your expertise. Thank you for considering Apple as a potential employer. We hope you will not be discouraged and will reach out again in the future. Warm regards, Apple Talent Acquisition',
    'Hello applicant, We are writing to you regarding your recent interviews for the Software Engineer position at Microsoft. We appreciate the time you spent with us and the insights you shared about your experience and qualifications. After careful consideration, we have decided not to proceed with an offer. This decision was particularly difficult due to the strength of your application and our conversations with you. We hope this outcome will not deter you from seeking opportunities with Microsoft in the future. We have many roles open throughout the year, and your skills could be a great fit for another position. Thank you for your interest in Microsoft and for the opportunity to get to know you. We wish you the best in your future professional endeavors. Kind regards, Microsoft Careers',
    ]

def generate_email(state, from_address, nums):
    emails = []
    dic = {
        'normal': EMAIL_BODIES, 'next_step': NEXT_STEP_EMAIL_BODIES,
        'offer': OFFER_EMAIL_BODIES, 'rejected': REJECTED_EMAIL_BODIES
    }
    for _ in range(nums):
        body = random.choice(dic[state])
        days_before = random.randint(0, 60)
        random_date = datetime.now() - timedelta(days=days_before)
        formatted_date = formatdate(timeval=mktime(random_date.timetuple()), localtime=False, usegmt=True)
        email_message = EmailMessage()
        email_message['Subject'] = 'Hello'
        email_message['From'] = from_address
        email_message['To'] = 'recipient@example.com'
        email_message['Date'] = formatted_date
        email_message.set_content(body)
        emails.append(email_message)
    return emails

def generate_mix_email(mbox_name, from_address, lst):
    normal, applied, next_step, offer, rejected = lst
    emails = []
    if normal:
        emails.extend(generate_email('normal', from_address, normal))
    if next_step:
        emails.extend(generate_email('next_step', from_address, normal))
    if offer:
        emails.extend(generate_email('offer', from_address, normal))
    if rejected:
        emails.extend(generate_email('rejected', from_address, normal))
    filename = mbox_name + '.mbox'
    mbox = mailbox.mbox(filename)
    mbox.lock()
    try:
        for email in emails:
            mbox.add(email)
        mbox.flush()
    finally:
        mbox.unlock()
