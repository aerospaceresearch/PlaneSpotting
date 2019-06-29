

def identifier1(df, tc): #Aircraft identification
    '''
    ADS-B type identifier function for Downlink Format 17 - 18 & Type Code 1 - 4
    These messages contain Aircraft identification data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if 17 <= df <= 18 and 1 <= tc <= 4:
        return True

def identifier2(df, tc):
    '''
    ADS-B type identifier function for Downlink Format 17 - 18 & Type Code 5 - 8
    These messages contain Surface Position data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if 17 <= df <= 18 and 5 <= tc <= 8:
        return True

def identifier3(df, tc): #airborne position with baro altitude
    '''
    ADS-B type identifier function for Downlink Format 17 - 18 & Type Code 9-18
    These messages contain Airborne Position with Barometric Altitude data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if 17 <= df <= 18 and 9 <= tc <= 18:
        return True

def identifier4(df, tc): #Airborne velocity
    '''
    ADS-B type identifier function for Downlink Format 17 - 18 & Type Code 19
    These messages contain Airborne Velocity data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if 17 <= df <= 18 and tc == 19:
        return True

def identifier5(df, tc): #Airborne Position with GNSS altitude
    '''
    ADS-B type identifier function for Downlink Format 17 - 18 & Type Code 20-22
    These messages contain Airborne Position with GNSS altitude data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if 17 <= df <= 18 and 20 <= tc <= 22:
        return True

def identifier6(df, tc): #Operation status
    '''
    ADS-B type identifier function for Downlink Format 17 - 18 & Type Code 31
    These messages contain Operation Status data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if 17 <= df <= 18 and tc == 31:
        return True

def identifier7(df, tc): #Enhanced Mode-S
    '''
    ADS-B type identifier function for Downlink Format 20 - 21
    These messages contain Enhanced Mode-S ADS-B data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if 20 <= df <= 21:
        return True

def identifier8(df, tc): #For squawk Ident msgs
    '''
    ADS-B type identifier function for Downlink Format 5
    These messages contain SQUAWK/IDENT data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if df == 5:
        return True

def identifier9(df, tc):
    '''
    ADS-B type identifier function for Downlink Format 0
    These messages contain Short Air to Air ACAS messages

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if df == 0:
        return True

def identifier10(df, tc):
    '''
    ADS-B type identifier function for Downlink Format 4
    These messages contain Altitude data

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if df == 4:
        return True

def identifier11(df, tc):
    '''
    ADS-B type identifier function for Downlink Format 5
    These messages contain Long ACAS messages

    :param df: Downlink Format
    :type df: Integer
    :param tc: Downlink Format
    :type tc: Integer
    :return: True/False
    :rtype: Boolean
    '''
    if df == 16:
        return True
