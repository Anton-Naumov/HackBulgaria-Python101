import unittest
from player_mixin import PlayerMixin
from spell import Spell
from weapon import Weapon


class PlayerMixinTests(unittest.TestCase):
    def setUp(self):
        self.player_with_no_mana = PlayerMixin(health=100, mana=0)
        self.dead_player = PlayerMixin(health=0, mana=50)

        self.player = PlayerMixin(health=100, mana=100)
        self.player2 = PlayerMixin(health=100, mana=100)
        self.w = Weapon(name="Axe", damage=20)
        self.s = Spell(name="Fireball", damage=30, mana_cost=50, cast_range=2)

    def test_is_alive_works(self):
        self.assertFalse(self.dead_player.is_alive())
        self.assertTrue(self.player_with_no_mana.is_alive())

    def test_get_health(self):
        self.assertEqual(self.player_with_no_mana.get_health(), 100)
        self.assertEqual(self.dead_player.get_health(), 0)

    def test_get_mana(self):
        self.assertEqual(self.player_with_no_mana.get_mana(), 0)
        self.assertEqual(self.dead_player.get_mana(), 50)

    def test_take_damage_works(self):
        with self.subTest('lethal damage'):
            self.player_with_no_mana.take_damage(100)
            self.assertFalse(self.player_with_no_mana.is_alive())

        with self.subTest('health_doesnt_become_negative'):
            player = PlayerMixin(health=10, mana=0)
            player.take_damage(20)
            self.assertEqual(player.get_health(), 0)

        with self.subTest('ONE DAMAGE OFF OF LETHAL'):
            self.player_with_no_mana._health = 100
            self.player_with_no_mana.take_damage(99)
            self.assertEqual(self.player_with_no_mana.get_health(), 1)

        with self.subTest('take floating point damage'):
            self.player_with_no_mana._health = 100
            self.player_with_no_mana.take_damage(49.9)
            self.assertEqual(self.player_with_no_mana.get_health(), 50.1)

    def test_take_healing(self):
        with self.subTest('heal dead player'):
            self.assertFalse(self.dead_player.take_healing(20))

        with self.subTest('heal to maximum health'):
            self.player_with_no_mana._health = 90
            self.assertTrue(self.player_with_no_mana.take_healing(20))
            self.assertEqual(self.player_with_no_mana.get_health(), 100)

        with self.subTest('heal a bit'):
            self.player_with_no_mana.take_damage(20)
            self.assertTrue(self.player_with_no_mana.take_healing(10))
            self.assertEqual(self.player_with_no_mana.get_health(), 90)

    def test_take_mana(self):
        self.dead_player._mana = 10
        self.dead_player.take_mana(30)
        self.assertEqual(self.dead_player.get_mana(), 40)
        self.dead_player.take_mana(30)
        self.assertEqual(self.dead_player.get_mana(), 50)

    def test_can_cast_is_called_without_being_overriden(self):
        with self.assertRaises(Exception):
            self.dead_player.can_cast()

    def test_attack_is_called_without_being_overriden(self):
        with self.assertRaises(Exception):
            self.dead_player.attack(by='weapon')

    def test_eq_returns_false_when_player1_has_weapon_and_player2_doesnt_have(self):
        self.player.equip(self.w)

        self.assertNotEqual(self.player, self.player2)

    def test_eq_returns_false_when_player1_has_spell_and_player2_doesnt_have(self):
        self.player.learn(self.s)

        self.assertNotEqual(self.player, self.player2)

    def test_eq_returns_false_when_weapons_are_not_the_same(self):
        self.player2.equip(Weapon(name="Knife", damage=20))
        self.player.equip(self.w)

        self.assertNotEqual(self.player, self.player2)

    def test_eq_returns_false_when_spells_are_not_the_same(self):
        self.player2.learn(Spell(name="FrostBall", damage=30, mana_cost=50, cast_range=2))
        self.player.learn(self.s)

        self.assertNotEqual(self.player, self.player2)

    def test_eq_returns_false_when_any_other_attrs_are_not_the_same(self):
        with self.subTest('when health is not the same'):
            player3 = PlayerMixin(health=50, mana=100)

            self.assertNotEqual(self.player, player3)

        with self.subTest('when max_health is not the same'):
            player3 = PlayerMixin(health=150, mana=100)
            player3._health = 100

            self.assertNotEqual(self.player, player3)

    def test_eq_returns_true(self):
        self.player.equip(self.w)
        self.player.learn(self.s)
        self.player2.equip(self.w)
        self.player2.learn(self.s)

        self.assertEqual(self.player, self.player2)

    def test_to_json(self):
        self.player.equip(self.w)

        expected = {
            'health': 100,
            'mana': 100,
            'weapon': self.w.to_json(),
            'spell': None
        }

        self.assertDictEqual(self.player.to_json(), expected)

    def test_from_json(self):
        json_dict = {
            'health': 100,
            'mana': 100,
            'weapon': None,
            'spell': self.s.to_json()
        }
        self.player.learn(self.s)

        self.assertEqual(PlayerMixin.from_json(json_dict), self.player)


if __name__ == '__main__':
    unittest.main()
