import service_email


if __name__ == '__main__':
    # notice 只能使用日本ip，不能使用香港ip
    cur_ServiceEmail = service_email.ServiceEmail('mlkteajx@fabrikamail.com', 'czmqfdcpY!4767')
    cur_ServiceEmail._get_email_from_firstmail_with_IMAP()
