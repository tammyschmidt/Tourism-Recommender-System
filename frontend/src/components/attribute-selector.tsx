import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Users, Wine, Baby, Bike, CreditCard, Car, Utensils, Truck, Users as GroupIcon, Phone, Table, ShoppingBag, Accessibility, Wifi, Sun } from "lucide-react"

interface AttributeSelectorProps {
  onAttributeChange: (attributes: string[]) => void
}

const restaurantAttributes = [
  { id: "Full Alcohol Bar", label: "Full Bar", icon: Wine, description: "Full alcohol bar available" },
  { id: "Free WiFi", label: "Free WiFi", icon: Wifi, description: "Free WiFi available" },
  { id: "Outdoor Seating", label: "Outdoor Seating", icon: Sun, description: "Outdoor seating available" },
  { id: "Good for Kids", label: "Kid Friendly", icon: Baby, description: "Good for children" },
  { id: "Take Out", label: "Take Out", icon: ShoppingBag, description: "Take-out service" },
  { id: "Delivery", label: "Delivery", icon: Truck, description: "Delivery service" },
  { id: "Reservations", label: "Reservations", icon: Phone, description: "Accepts reservations" },
  { id: "Credit Card Accepted", label: "Credit Cards", icon: CreditCard, description: "Accepts credit cards" },
  { id: "Wheelchair Accessible", label: "Wheelchair Accessible", icon: Accessibility, description: "Wheelchair accessible" },
  { id: "Good for Groups", label: "Good for Groups", icon: GroupIcon, description: "Good for groups" },
  { id: "Catering", label: "Catering", icon: Utensils, description: "Catering services" },
  { id: "Dogs allowed", label: "Dog Friendly", icon: Users, description: "Dogs allowed" },
  { id: "TV", label: "Has TV", icon: Users, description: "Television available" },
  { id: "Happy Hour", label: "Happy Hour", icon: Wine, description: "Happy hour specials" },
  { id: "Lot Parking", label: "Parking Lot", icon: Car, description: "Parking lot available" },
  { id: "Street Parking", label: "Street Parking", icon: Car, description: "Street parking available" },
  { id: "Bike Parking", label: "Bike Parking", icon: Bike, description: "Bicycle parking available" },
  { id: "Table Service", label: "Table Service", icon: Table, description: "Table service" }
]

export default function AttributeSelector({ onAttributeChange }: Readonly<AttributeSelectorProps>) {
  const [selectedAttributes, setSelectedAttributes] = useState<string[]>([])

  const handleAttributeSelect = (attributeId: string) => {
    const newSelectedAttributes = selectedAttributes.includes(attributeId)
      ? selectedAttributes.filter(id => id !== attributeId)
      : [...selectedAttributes, attributeId]
    
    console.log('DEBUG: AttributeSelector - Selected attributes:', newSelectedAttributes)
    setSelectedAttributes(newSelectedAttributes)
    onAttributeChange(newSelectedAttributes)
    console.log('DEBUG: AttributeSelector - Called onAttributeChange with:', newSelectedAttributes)
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
        {restaurantAttributes.map((attribute) => {
          const Icon = attribute.icon
          const isSelected = selectedAttributes.includes(attribute.id)

          return (
            <Button
              key={attribute.id}
              variant={isSelected ? "default" : "outline"}
              className="h-auto p-3 flex flex-col items-start text-left"
              onClick={() => handleAttributeSelect(attribute.id)}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className="w-4 h-4" />
                <span className="font-medium text-sm">{attribute.label}</span>
              </div>
              <span className="text-xs opacity-80">{attribute.description}</span>
            </Button>
          )
        })}
      </div>
    </div>
  )
}