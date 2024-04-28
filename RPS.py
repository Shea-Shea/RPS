import random
# import numpy as np

# Code is set up to assume the first play is yours. I.e. PR means you played paper, opponent played rock.


def player(
        prev_play, opponent_history=[],
        my_history=[],
        my_call_count=[0],
        reset_count=[0], strat_history=[]):

    my_call_count[0] += 1
    win_percentage = 0
    strat = False

    # Reset history and conters every 1000 games
    if my_call_count[0] == 1001:
        my_history.clear()
        opponent_history.clear()
        strat_history.clear()
        my_call_count[0] = 1
        reset_count[0] += 1

    opponent_history.append(prev_play)
    winning_plays = {'R': 'P', 'S': 'R', 'P': 'S'}
    scoring = {'PR': 1, 'RS': 1, 'SP': 1, 'RP': -1,
               'SR': -1, 'PS': -1, 'RR': 0, 'PP': 0, 'SS': 0}

    # Default play for the first game. This should only be used once.
    if not my_history:
        guess = 'R'

    # Run everything below after the first game is played.
    else:
        filtered_opp_history = opponent_history[1:]   # Remove blank play from history
        wins, loss, ties = 0, 0, 0
        strat_choice, strat_1_count, strat_2_count = 0, 0, 0

        if len(my_history) > 19:  # Make sure enough games have been played to get an accurate read of strategy performance.
            strat = True
            for number in range(-19, 0):
                if scoring[my_history[number]+filtered_opp_history[number]] == 1:
                    wins += 1
                elif scoring[my_history[number]+filtered_opp_history[number]] == -1:
                    loss += 1
                elif scoring[my_history[number]+filtered_opp_history[number]] == 0:
                    ties += 1

                if loss == 0:
                    win_percentage = 1.0
                else:
                    win_percentage = wins / (wins + loss)

                if strat_history[number] == 1:
                    strat_1_count += 1
                elif strat_history[number] == 2:
                    strat_2_count += 1

            # If strategy 1 performing poorly switch to strategy 2
            if win_percentage < 0.60 and strat_1_count > strat_2_count:
                strat_choice = 2
                strat_history.append(strat_choice)
            # If strategy 2 performing poorly switch to strategy 1
            if win_percentage < 0.60 and strat_2_count > strat_1_count:
                strat_choice = 1
                strat_history.append(strat_choice)

        # Default strategy - using bayes theorem to predict opponents next move based on game history.
        if len(filtered_opp_history) > 10 and strat_history[-1] == 1:
            guess = winning_plays[bayes(my_history, filtered_opp_history)]

        # If first condition not met, set guess to a random to avoid local variable error
        else:
            guess = random.choice(['R', 'P', 'S'])

    # Make sure strategy has been set. This will happen after a defined number of games have been played.
    # The following block is designed to beat a player who looks at sequence of the last play you made
    # plus the possible next play (R,P, or S) and determines which one occurs the most in your history and plays against that.
    # i.e. if your previous is R and your possible next plays are R,P,S then it will look for the counts of RR, RP, RS in the your history.
    # If RP has the largest value of occurence then it will predict you play P next so this function will return S to beat that prediction
    # of your opponent.
    if strat:
        if strat_history[-1] == 2:  # If strategy 1 if losing too many games in a row this section will run.

            possible_plays = ['R', 'P', 'S']
            storage = {'R': 0, 'P': 0, 'S': 0}
            trick_play = {'R': 'S', 'P': 'R', 'S': 'P'}
            my_hist_string = ''.join(my_history)

            # Count number of times my previous play and the next possible (R,P,S) appear
            # in my history in that order and place in a dictionary
            for play in possible_plays:
                my_possible_next = my_history[-1] + play
                my_possible_next_count = len([i for i in range(
                    len(my_hist_string)) if my_hist_string.startswith(my_possible_next, i)])
                storage[play] = my_possible_next_count  # Store play recurrence

            # Find the possible play sequence with the highest recurrence
            max_possible = max(storage, key=storage.get)
            guess = trick_play[max_possible]  # Play the opposite of what you believe the opponent will play.

    my_history.append(guess)

    # If not strategy has been set (desired qty. of games has not been played), set the default strategy to 1.
    if not strat:
        strat_history.append(1)

    return guess

################# Predicting Plays using Bayes Theorem #########################
# Almost all of the below is the same code repeated and slightly modified for different conditions
# in order to account for most scenarios and return a play with the most probable likelihood of winning.


def bayes(my_hist, opp_history):  # Function for calculating the probable next play by opponent

    if len(my_hist) == len(opp_history):
        my_hist_string = ''.join(my_hist)
        opp_history_string = ''.join(opp_history)
    else:
        print('Error: The lengths of the histories do not match.')
        exit()

    # For P(A|B) the below is a list holding the possible values of A.
    possible_next = ['R', 'P', 'S']

    # Conditiionals. For P(A|B) the following three variables are B.
    prev_two_plays = opp_history_string[-2:]
    prev_play = opp_history[-1]
    my_prev_play = my_hist[-1]
    my_prev_two_plays = my_hist_string[-2:]

    # Declare dicitonary to store all the probability values to be calculated
    posterior_dicts = {"Previous Two": {'R': None, 'P': None, 'S': None},
                       "Previous": {'R': None, 'P': None, 'S': None},
                       "My Previous": {'R': None, 'P': None, 'S': None},
                       "My Previous Two": {'R': None, 'P': None, 'S': None},
                       "My Likely Next": {'R': None, 'P': None, 'S': None},
                       "Previous Match": {'R': None, 'P': None, 'S': None}}

    prev_two_plays_index = [i for i in range(
        len(opp_history_string)) if opp_history_string.startswith(prev_two_plays, i)]
    prev_play_index = [i for i in range(
        len(opp_history_string)) if opp_history_string.startswith(prev_play, i)]
    my_prev_play_index = [i for i in range(
        len(my_hist_string)) if my_hist_string.startswith(my_prev_play, i)]
    my_prev_two_plays_index = [i for i in range(
        len(my_hist_string)) if my_hist_string.startswith(my_prev_two_plays, i)]
    prev_match_index = [i for i in range(len(my_hist_string)) if opp_history_string.startswith(
        opp_history[-1], i) and my_hist_string.startswith(my_hist[-1], i)]
    # print(prev_match_index)

    # Marginal. P(B)
    P_prev_two = opp_history_string.count(
        prev_two_plays) / (len(opp_history_string)-1)
    P_prev = opp_history_string.count(
        prev_play) / len(opp_history_string)
    P_my_prev = my_hist_string.count(
        my_prev_play) / len(my_hist_string)
    P_my_prev_two = my_hist_string.count(
        my_prev_play) / (len(my_hist_string)-1)
    P_prev_match = len(prev_match_index) / len(my_hist_string)

    # Calculate conditional probabilities for the the possible next plays given the opponents previous TWO plays
    for next in possible_next:
        next_count = 0
        for index in prev_two_plays_index:
            if len(opp_history_string)-index > 2:
                # print(f'The len of the string is {
                # len(opp_history_string)}. The index is: {index}')
                # print(opp_history_string[index + 2])

                # Count number of times that the previous two plays are found IMMEDIATLEY preceding the possible next play in the recorded history
                if opp_history_string[index+2] == next:
                    next_count += 1
        if opp_history_string.count(next) == 0:
            P_prior = 0
            P_prev_two_given_next = 0
            posterior_prev_two = 0
        else:
            # Prior. P(A)
            P_prior = opp_history_string.count(next) / len(opp_history_string)
            # Likelihood
            P_prev_two_given_next = next_count / opp_history_string.count(next)
            # Posterior
            posterior_prev_two = P_prev_two_given_next * P_prior / P_prev_two
            # Append the calculated probabilities to the appropriate dictionary keys
        posterior_dicts['Previous Two'][next] = posterior_prev_two
        # print(f' The posterior is {posterior_prev_two} | The likelihood is {
        # P_prev_two_given_next} | The prior is {P_prior} | The marginal is {P_prev_two}')

    # Calculate conditional probabilities for the the possible next plays given the previous opponents PREVIOUS play
    for next in possible_next:
        next_count = 0
        for index in prev_play_index:
            if len(opp_history_string)-index > 1:

                # Count number of times that the previous play is found IMMEDIATLEY preceding the possible next play in the recorded history
                if opp_history_string[index+1] == next:
                    next_count += 1
        if opp_history_string.count(next) == 0:
            P_prior = 0
            P_prev_given_next = 0
            posterior_prev = 0
        else:
            # Prior. P(A)
            P_prior = opp_history_string.count(next) / len(opp_history_string)
            # Likelihood
            P_prev_given_next = next_count / opp_history_string.count(next)
            # Posterior
            posterior_prev = P_prev_given_next * P_prior / P_prev
            # Append the calculated probabilities to the appropriate dictionary keys
        posterior_dicts['Previous'][next] = posterior_prev
        # print(f' The posterior is {posterior_prev} | The likelihood is {
        # P_prev_given_next} | The prior is {P_prior} | The marginal is {P_prev}')

    # Calculate conditional probabilities for the the possible next plays given MY PREVIOUS play
    for next in possible_next:
        next_count = 0
        my_next_count = 0
        for index in my_prev_play_index:
            if len(my_hist_string)-index > 1:

                # Count number of times that the previous play is found IMMEDIATLEY preceding the possible next play in the recorded history
                if opp_history_string[index+1] == next:
                    next_count += 1

                # Same as above but for my history
                if my_hist_string[index+1] == next:
                    my_next_count += 1
        if opp_history_string.count(next) == 0:
            P_prior = 0
            P_my_prev_given_next = 0
            posterior_my_prev = 0

        else:
            # Prior. P(A)
            P_prior = opp_history_string.count(next) / len(opp_history_string)
            # Likelihood
            P_my_prev_given_next = next_count / opp_history_string.count(next)
            # Posterior
            posterior_my_prev = P_my_prev_given_next * P_prior / P_my_prev
            # Append the calculated probabilities to the appropriate dictionary keys
        posterior_dicts['My Previous'][next] = posterior_my_prev
        # print(f' The posterior is {posterior_prev_two} | The likelihood is {
        # P_prev_two_given_next} | The prior is {P_prior} | The marginal is {P_prev}')
    # print(posterior_dicts)

        ##### Repeat same code above but solve for my likely next play given the history #####
        if my_hist_string.count(next) == 0:
            P_my_prior = 0
            P_my_prev_given_my_next = 0
            my_posterior_my_prev = 0
        else:
            # Prior. P(A)
            P_my_prior = my_hist_string.count(next) / len(my_hist_string)
            # Likelihood
            P_my_prev_given_my_next = my_next_count / \
                my_hist_string.count(next)
            # Posterior
            my_posterior_my_prev = P_my_prev_given_my_next * P_my_prior / P_my_prev
            # Append the calculated probabilities to the appropriate dictionary keys

        my_next = {'R': 'P', 'P': 'S', 'S': 'R'}
        posterior_dicts['My Likely Next'][my_next[next]
                                          ] = my_posterior_my_prev
        # print(f' my history: {my_hist}')
        # print(f'Opponent history: {opp_history}')
        # if len(my_hist) % 10 == 0:
        # print(posterior_dicts)
        # print(f' MY Likely Next: The posterior is {my_posterior_my_prev} | The likelihood is {
        # P_my_prev_given_my_next} | The prior is {P_my_prior} | The marginal is {P_my_prev}')

    # Calculate conditional probabilities for opponents possible next plays given MY PREVIOUS TWO plays
    for next in possible_next:
        next_count = 0
        for index in my_prev_two_plays_index:
            if len(my_hist_string)-index > 2:

                # Count number of times that the previous play is found IMMEDIATLEY preceding the possible next play in the recorded history
                if opp_history_string[index+2] == next:
                    next_count += 1
        # Set conditiion to avoid divide by zero errors.
        if opp_history_string.count(next) == 0:
            P_prior = 0
            P_my_prev_two_given_next = 0
            posterior_my_prev_two = 0
        else:
            # Prior. P(A)
            P_prior = opp_history_string.count(next) / len(opp_history_string)
            # Likelihood
            P_my_prev_two_given_next = next_count / \
                opp_history_string.count(next)
            # Posterior
            posterior_my_prev_two = P_my_prev_two_given_next * P_prior / P_my_prev_two
            # Append the calculated probabilities to the appropriate dictionary keys
        posterior_dicts['My Previous Two'][next] = posterior_my_prev_two

################# Conditional Probabilites given results of previous match ######################

    # Calculate conditional probabilities for the the possible next plays given the result of the previous match in format 'OpponentPlayer'
    for next in possible_next:
        next_count = 0
        for index in prev_match_index:
            # Could use opp_hist string for this case as well since there are the same length
            if len(my_hist_string)-index > 1:

                # Count number of times that the previous play is found IMMEDIATLEY preceding the possible next play in the recorded history
                if opp_history_string[index+1] == next:
                    next_count += 1
        # Set conditiion to avoid divide by zero errors.
        if opp_history_string.count(next) == 0:
            P_prior = 0
            P_prev_match_given_next = 0
            posterior_prev_match = 0
        else:
            # Prior. P(A)
            P_prior = opp_history_string.count(next) / len(opp_history_string)
            # Likelihood
            P_prev_match_given_next = next_count / \
                opp_history_string.count(next)
            # Posterior
            posterior_prev_match = P_prev_match_given_next * P_prior / P_prev_match
            # Append the calculated probabilities to the appropriate dictionary keys
        posterior_dicts['Previous Match'][next] = posterior_prev_match
        # print(f' The posterior is {posterior_prev_match} | The likelihood is {
        # P_prev_match_given_next} | The prior is {P_prior} | The marginal is {P_prev_match}')

    probable_key, probable_value = max(((key, value) for dicts in posterior_dicts.values(
    ) for key, value in dicts.items()), key=lambda x: x[1])
    # print(posterior_dicts)
    # print(probable_key)

    return probable_key
