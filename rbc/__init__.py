from otree.api import *
import random
from decimal import Decimal
from starlette.responses import HTMLResponse
from starlette.exceptions import HTTPException
from otree import constants as otree_constants

# All tunable parameters live in params.py — edit there, not here.
from params import ENDOWMENT, COST_DIVISOR, NUM_ROUNDS, PENALTY_LOW


doc = """
Reversed Beauty Contest. Each round players choose a number x in [0, 100]; cost is
x^2/k; a fixed penalty L is paid by anyone whose x is strictly below the group median.
At the China site (site 1), each official session runs a single treatment and forms either three groups
of 5 or one group of 15. Comprehension quiz at
start; SOEP risk Likert in exit survey; payment is the show-up fee plus the earnings
of one randomly selected round.
"""


class C(BaseConstants):
    NAME_IN_URL = 'rbc'
    # Group size is treatment-specific, so groups are formed dynamically on the
    # first wait page rather than through this static constant.
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = NUM_ROUNDS
    ENDOWMENT = ENDOWMENT
    K = COST_DIVISOR


class Subsession(BaseSubsession):
    groups_formed = models.IntegerField(initial=0)


def session_num_rounds(obj):
    return obj.session.config.get('num_rounds', C.NUM_ROUNDS)


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        players = subsession.get_players()
        expected_session_size = subsession.session.config.get('expected_session_size')
        if expected_session_size is not None and len(players) != expected_session_size:
            raise RuntimeError(
                f"This treatment requires exactly {expected_session_size} participants, "
                f"but the session was created with {len(players)}."
            )

        config = subsession.session.config
        rounds = session_num_rounds(subsession)
        if type(rounds) is not int or not 1 <= rounds <= C.NUM_ROUNDS:
            raise RuntimeError(f'num_rounds must be an integer from 1 to {C.NUM_ROUNDS}.')
        sizes = config.get('group_sizes')
        size = config.get('group_size')
        if sizes is not None:
            if not isinstance(sizes, list) or not sizes or any(type(n) is not int or n < 3 or n % 2 == 0 for n in sizes) or sum(sizes) != len(players):
                raise RuntimeError('group_sizes must contain odd sizes >= 3 and sum to the participant count.')
        elif type(size) is not int or size < 3 or size % 2 == 0 or len(players) % size:
            raise RuntimeError('group_size must be odd, >= 3, and divide the participant count.')
        if C.K <= 0 or config.get('penalty', PENALTY_LOW) < 0:
            raise RuntimeError('Cost divisor must be positive and penalty nonnegative.')
        if config['real_world_currency_per_point'] <= 0 or config['participation_fee'] < 0:
            raise RuntimeError('Payment conversion must be positive and participation fee nonnegative.')

        # One common paid round for the whole session (announced at the end),
        # so every participant is paid for the same randomly drawn round.
        paid_round_max = session_num_rounds(subsession)
        common_paid_round = random.randint(1, paid_round_max)
        for p in players:
            p.participant.paid_round = common_paid_round


def group_by_arrival_time_method(subsession: Subsession, waiting_players):
    group_sizes = subsession.session.config.get('group_sizes')
    if group_sizes:
        next_group = subsession.groups_formed
        if next_group >= len(group_sizes):
            return
        target_size = group_sizes[next_group]
        if len(waiting_players) >= target_size:
            subsession.groups_formed += 1
            return waiting_players[:target_size]

    group_size = subsession.session.config.get('group_size')
    if group_size is not None and len(waiting_players) >= group_size:
        return waiting_players[:group_size]


def player_group_size(player):
    return len(player.group.get_players())


class Group(BaseGroup):
    median_x = models.FloatField()


class Player(BasePlayer):
    consent_given = models.BooleanField(
        label="我同意参加本实验。",
        blank=True,  # validated in Consent.error_message instead, so we get a friendlier message
    )

    x_choice = models.IntegerField(
        min=0, max=100,
        label='请选择一个 0 到 100 之间的数字',
    )
    belief_median = models.IntegerField(
        min=0, max=100,
        label='你认为本轮小组的中位数会是多少？',
    )
    cost = models.FloatField(initial=0)
    penalty_paid = models.FloatField(initial=0)
    round_payoff = models.FloatField(initial=0)

    quiz_below_median = models.StringField(
        choices=[
            ('yes', '是 — 需要支付罚金。'),
            ('no', '否 — 不需要支付罚金。'),
        ],
        label="如果你的数字严格低于小组中位数，你需要支付罚金吗？",
        widget=widgets.RadioSelect,
    )
    quiz_match_median = models.StringField(
        choices=[
            ('penalty', '是 — 需要支付罚金。'),
            ('no_penalty', '否 — 不需要支付罚金。'),
            ('half', '需要支付一半罚金。'),
        ],
        label="如果你的数字恰好等于小组中位数，你需要支付罚金吗？",
        widget=widgets.RadioSelect,
    )
    quiz_cost = models.StringField(
        choices=[
            ('higher', '数字越大，成本越高。'),
            ('lower', '数字越小，成本越高。'),
            ('same', '所有数字的成本相同。'),
        ],
        label="你选择的数字如何影响你的成本？",
        widget=widgets.RadioSelect,
    )
    quiz_equal_earnings = models.StringField(
        choices=[
            ('no_penalty_formula', '100 − x²/200'),
            ('penalty_formula', '100 − x²/200 − 20'),
            ('linear_formula', '100 − x − 20'),
        ],
        label=(
            "假设你的数字是 x，小组中位数是 y，罚金 = 20，且 x = y。"
            "你本轮的收益是多少？"
        ),
        widget=widgets.RadioSelect,
    )
    quiz_below_earnings = models.StringField(
        choices=[
            ('no_penalty_formula', '100 − x²/200'),
            ('penalty_formula', '100 − x²/200 − 20'),
            ('linear_formula', '100 − x − 20'),
        ],
        label=(
            "假设你的数字是 x，小组中位数是 y，罚金 = 20，且 x < y。"
            "你本轮的收益是多少？"
        ),
        widget=widgets.RadioSelect,
    )
    quiz_fixed_penalty = models.StringField(
        choices=[
            ('fixed', '罚金是相同的固定金额 L。'),
            ('distance', 'x 比 y 低得越多，罚金越大。'),
            ('half', '罚金是 L 的一半。'),
        ],
        label="如果 x < y，罚金是否取决于 x 比 y 低多少？",
        widget=widgets.RadioSelect,
    )


    survey_risk = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        min=0, max=10,
        label=(
            "Q1. 总体而言，你如何评价自己承担风险的意愿？"
            "（0 = 完全不愿意，10 = 非常愿意）"
        ),
        widget=widgets.RadioSelectHorizontal,
    )
    survey_strategy = models.LongStringField(
        label="Q6. 每一轮你是如何决定选择哪个数字的？",
    )
    survey_use_median = models.StringField(
        choices=[
            ('always', '总是'),
            ('often', '经常'),
            ('sometimes', '有时'),
            ('never', '从不'),
        ],
        label="Q2. 你是否利用上一轮的中位数来帮助你做决策？",
        widget=widgets.RadioSelect,
    )
    survey_median_importance = models.StringField(
        choices=[
            ('very', '非常重要'),
            ('somewhat', '比较重要'),
            ('not_much', '不太重要'),
            ('not_at_all', '完全不重要'),
        ],
        label="Q3. 上一轮的中位数在你的决策中有多重要？",
        widget=widgets.RadioSelect,
    )
    survey_use_prior_medians = models.StringField(
        choices=[
            ('always', '总是'),
            ('often', '经常'),
            ('sometimes', '有时'),
            ('never', '从不'),
        ],
        label="Q4. 你是否利用之前两轮或更多轮的中位数来帮助你做决策？",
        widget=widgets.RadioSelect,
    )
    survey_prior_medians_importance = models.StringField(
        choices=[
            ('very', '非常重要'),
            ('somewhat', '比较重要'),
            ('not_much', '不太重要'),
            ('not_at_all', '完全不重要'),
        ],
        label="Q5. 之前两轮或更多轮的中位数在你的决策中有多重要？",
        widget=widgets.RadioSelect,
    )
    survey_best = models.StringField(
        choices=[
            ('all_zero', '所有人都选 0'),
            ('all_high', '所有人都选较高的数字'),
            ('mixed_low_high', '一些人选较低的数字，一些人选较高的数字'),
            ('other', '其他'),
        ],
        label="Q7. 你认为每一轮对小组来说最好的结果是什么？",
        widget=widgets.RadioSelect,
    )
    survey_best_other = models.StringField(
        label="如选其他，请说明：",
        blank=True,
    )
    survey_gender = models.StringField(
        choices=[
            ('male', '男'),
            ('female', '女'),
            ('nonbinary', '非二元性别'),
            ('prefer_not', '不愿透露'),
        ],
        label="Q10. 您的性别",
        widget=widgets.RadioSelect,
    )
    survey_prior_bc = models.StringField(
        choices=[
            ('yes', '是'),
            ('no', '否'),
            ('unsure', '不确定'),
        ],
        label="Q8. 你以前参加过选美竞赛（Beauty Contest）类实验吗？",
        widget=widgets.RadioSelect,
    )
    survey_game_theory = models.StringField(
        choices=[
            ('formal', '修过正式课程'),
            ('self_study', '自学过'),
            ('no', '没有'),
        ],
        label="Q9. 你学过博弈论或实验经济学吗？",
        widget=widgets.RadioSelect,
    )
    survey_age = models.StringField(
        choices=[(str(a), str(a)) for a in range(17, 30)] + [('30+', '30 岁及以上')],
        label="Q11. 年龄",
    )


def set_payoffs(group: Group):
    L = group.session.config.get('penalty', PENALTY_LOW)
    players = group.get_players()
    sorted_choices = sorted([p.x_choice for p in players])
    n = len(sorted_choices)
    if n % 2 == 1:
        median = float(sorted_choices[n // 2])
    else:
        median = (sorted_choices[n // 2 - 1] + sorted_choices[n // 2]) / 2.0
    group.median_x = median
    for p in players:
        cost = Decimal(p.x_choice ** 2) / Decimal(str(C.K))
        p.cost = float(cost)
        p.penalty_paid = float(L) if p.x_choice < median else 0.0
        p.round_payoff = float(
            Decimal(str(C.ENDOWMENT)) - cost - Decimal(str(p.penalty_paid))
        )


def settle_payment(player: Player):
    """Book only the selected round, once the participant submits the survey.

    Convert to Currency before assignment: repeated calls then have an exact
    zero delta, including half-point payoffs. Rendering Payment never writes.
    """
    paid_player = player.in_round(player.participant.paid_round)
    player.payoff = cu(Decimal(str(paid_player.round_payoff)))


# ============ Pages ============

class ParticipantPage(Page):
    """oTree 5.11.5 adapter: reject forced advancement before fields are populated.

    Admin release is allowed only on Welcome. Other pages require real responses.
    This deliberately guards the HTTP submission path, not only the admin button.
    """
    def post(self):
        if self._form_data.get(otree_constants.timeout_happened) and type(self).__name__ != "Welcome":
            return HTMLResponse("本实验禁止强制推进或自动代填答案。请让参与者完成当前页面。", status_code=409)
        return super().post()


class GroupFormationWaitPage(WaitPage):
    group_by_arrival_time = True
    title_text = "等待分组"
    body_text = "请等待同组参与者到齐。完成分组后，请继续等待实验员统一开始实验。"

    @staticmethod
    def is_displayed(player: Player):
        return (
            player.round_number == 1
            and (
                player.session.config.get('group_size') is not None
                or player.session.config.get('group_sizes') is not None
            )
        )

class Welcome(ParticipantPage):
    @staticmethod
    def error_message(player, values):
        return "请等待实验员统一开始实验。"

    @staticmethod
    def before_next_page(player, timeout_happened):
        if not timeout_happened:
            raise HTTPException(409, "请等待实验员统一开始实验。")
        if not player.session.vars.get('experiment_started'):
            if not all(p._current_page_name == 'Welcome' for p in player.session.get_participants()):
                raise HTTPException(409, "必须等所有参与者到达欢迎页后才能开始。")
            player.session.vars['experiment_started'] = True

    @staticmethod
    def is_displayed(player: Player):
        return (
            player.round_number == 1
            and player.session.config.get('show_welcome', False)
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            n=player_group_size(player),
            num_rounds=session_num_rounds(player),
        )


class Consent(ParticipantPage):
    form_model = 'player'
    form_fields = ['consent_given']

    @staticmethod
    def is_displayed(player: Player):
        return (
            player.round_number == 1
            and player.session.config.get('show_consent', True)
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(num_rounds=session_num_rounds(player))

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('consent_given'):
            return "你必须勾选同意框才能参加实验。"


class Instructions(ParticipantPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        group_size = player_group_size(player)
        return dict(
            L=player.session.config.get('penalty', PENALTY_LOW),
            E=C.ENDOWMENT,
            K=C.K,
            n=group_size,
            other_players=group_size - 1,
            num_rounds=session_num_rounds(player),
            point_value=player.session.config.get('real_world_currency_per_point', 1),
            participation_fee=f"{Decimal(player.session.config['participation_fee']):.2f}",
            elicit_belief=player.session.config.get('elicit_belief', False),
        )


class Quiz(ParticipantPage):
    form_model = 'player'
    form_fields = [
        'quiz_match_median',
        'quiz_cost',
        'quiz_equal_earnings',
        'quiz_below_earnings',
        'quiz_fixed_penalty',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        # (字段, 正确答案, 页面题号)
        correct = [
            ('quiz_match_median', 'no_penalty', 1),
            ('quiz_cost', 'higher', 2),
            ('quiz_equal_earnings', 'no_penalty_formula', 3),
            ('quiz_below_earnings', 'penalty_formula', 4),
            ('quiz_fixed_penalty', 'fixed', 5),
        ]
        wrong = sorted({num for k, v, num in correct if values.get(k) != v})
        if wrong:
            nums = "、".join(str(n) for n in wrong)
            return f"第 {nums} 题答错了。请重新阅读规则后再试一次。"

    @staticmethod
    def vars_for_template(player: Player):
        # 含 instructions_content.html（页内"查看规则"折叠块）需要的全部变量
        group_size = player_group_size(player)
        return dict(
            L=player.session.config.get('penalty', PENALTY_LOW),
            E=C.ENDOWMENT,
            K=C.K,
            n=group_size,
            other_players=group_size - 1,
            num_rounds=session_num_rounds(player),
            point_value=player.session.config.get('real_world_currency_per_point', 1),
            participation_fee=f"{Decimal(player.session.config['participation_fee']):.2f}",
            elicit_belief=player.session.config.get('elicit_belief', False),
        )


class Belief(ParticipantPage):
    form_model = 'player'
    form_fields = ['belief_median']

    @staticmethod
    def is_displayed(player: Player):
        return (
            player.round_number <= session_num_rounds(player)
            and player.session.config.get('elicit_belief', False)
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number=player.round_number,
            num_rounds=session_num_rounds(player),
        )


class Choice(ParticipantPage):
    form_model = 'player'
    form_fields = ['x_choice']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number <= session_num_rounds(player)

    @staticmethod
    def error_message(player: Player, values):
        if values.get('x_choice') is None:
            return "请选择一个数字并确认提交。"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            L=player.session.config.get('penalty', PENALTY_LOW),
            E=C.ENDOWMENT,
            K=C.K,
            round_number=player.round_number,
            num_rounds=session_num_rounds(player),
        )


class WaitForGroup(WaitPage):
    title_text = "等待同组选择"
    body_text = "你的选择已提交，请等待同组其他参与者。所有组员提交后将显示本轮结果。"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number <= session_num_rounds(player)

    @staticmethod
    def after_all_players_arrive(group: Group):
        set_payoffs(group)


class Results(ParticipantPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number <= session_num_rounds(player)

    @staticmethod
    def vars_for_template(player: Player):
        median = player.group.median_x
        num_rounds = session_num_rounds(player)
        return dict(
            x=player.x_choice,
            cost=f"{Decimal(str(player.cost)):.3f}",
            median=int(median) if median == int(median) else round(median, 1),
            below_median=player.x_choice < median,
            penalty=int(player.penalty_paid),
            round_payoff=f"{Decimal(str(player.round_payoff)):.3f}",
            E=C.ENDOWMENT,
            K=C.K,
            L=player.session.config.get('penalty', PENALTY_LOW),
            round_number=player.round_number,
            num_rounds=num_rounds,
            is_last_round=player.round_number == num_rounds,
        )


class Survey(ParticipantPage):
    form_model = 'player'
    form_fields = [
        'survey_risk',
        'survey_use_median',
        'survey_median_importance',
        'survey_use_prior_medians',
        'survey_prior_medians_importance',
        'survey_strategy',
        'survey_best',
        'survey_best_other',
        'survey_prior_bc',
        'survey_game_theory',
        'survey_gender',
        'survey_age',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == session_num_rounds(player)

    @staticmethod
    def error_message(player: Player, values):
        # 其余题目通过必填校验；"其他请说明"仅在 Q7 选 other 时必填
        if values.get('survey_best') == 'other' and not (values.get('survey_best_other') or '').strip():
            return "你在 Q7 选择了\"其他\"，请在说明栏填写具体内容。"

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        settle_payment(player)


class Payment(ParticipantPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == session_num_rounds(player)

    @staticmethod
    def vars_for_template(player: Player):
        paid_round = player.participant.paid_round
        paid_amount = player.payoff
        fee = player.session.config.get('participation_fee', 0)
        point_value = player.session.config.get('real_world_currency_per_point', 1)
        # Use exactly the same conversion as the administrator Payments table.
        bonus = player.participant.payoff_in_real_world_currency()
        total = player.participant.payoff_plus_participation_fee()
        return dict(
            paid_round=paid_round,
            paid_amount=f"{Decimal(paid_amount):.3f}",
            point_value=point_value,
            bonus=f"{Decimal(bonus):.2f}",
            participation_fee=f"{Decimal(fee):.2f}",
            total=f"{Decimal(total):.2f}",
        )


page_sequence = [
    GroupFormationWaitPage,
    Welcome,
    Consent,
    Instructions,
    Quiz,
    Belief,
    Choice,
    WaitForGroup,
    Results,
    Survey,
    Payment,
]
